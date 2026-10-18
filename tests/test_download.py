"""Testes do 01_download.py com um servidor HTTP local que imita o FTP do IBGE.

Rodar: pytest -q
"""

import csv
import importlib.util
import io
import sys
import threading
import zipfile
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
import yaml

RAIZ = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("download", RAIZ / "src" / "01_download.py")
dl = importlib.util.module_from_spec(spec)
sys.modules["download"] = dl  # necessário para o @dataclass funcionar
spec.loader.exec_module(dl)
dl.TENTATIVAS = 1  # testes rápidos


def _zip_bytes(nome_interno: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(nome_interno, b"conteudo de teste")
    return buf.getvalue()


@pytest.fixture()
def servidor(tmp_path):
    """Cria /pense/2019/xls e /pense/2024/xlsx com nomes no padrão do IBGE."""
    www = tmp_path / "www"
    d19 = www / "pense" / "2019" / "xls"
    d24 = www / "pense" / "2024" / "xlsx"
    d19.mkdir(parents=True)
    d24.mkdir(parents=True)

    (d19 / "Guia_Tabelas_PeNSE_2019_20260615.xls").write_bytes(b"guia19")
    (d19 / "Tema_09_Seguranca_20260615.xls").write_bytes(b"seg19")
    (d19 / "Tema_09_Seguranca_20220512.xls").write_bytes(b"versao antiga")
    (d19 / "Tema_03_Alimentacao_20260615.xls").write_bytes(b"nao deve baixar")

    (d24 / "Guia_Tabelas_PeNSE_2024_20260525.xlsx").write_bytes(b"guia24")
    (d24 / "Tema_09_Seguranca_XLSX_20260525.zip").write_bytes(_zip_bytes("tabela_9.1.xlsx"))

    handler = partial(SimpleHTTPRequestHandler, directory=str(www))
    handler.log_message = lambda *a, **k: None
    srv = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


@pytest.fixture()
def config(tmp_path, servidor):
    """fontes.yaml real, com as URLs do IBGE trocadas pelo servidor local."""
    cfg = yaml.safe_load((RAIZ / "config" / "fontes.yaml").read_text(encoding="utf-8"))
    for ed in cfg["edicoes"].values():
        ed["base_url"] = ed["base_url"].replace("https://ftp.ibge.gov.br", servidor)
    p = tmp_path / "fontes.yaml"
    p.write_text(yaml.safe_dump(cfg, allow_unicode=True), encoding="utf-8")
    return p


def _manifesto(saida):
    with (saida / "manifesto.csv").open(encoding="utf-8") as f:
        return {(r["edicao"], r["tema"]): r for r in csv.DictReader(f)}


def test_baixa_extrai_e_registra(config, tmp_path):
    saida = tmp_path / "raw"
    rc = dl.executar(config, saida, temas=["guia", "tema_09"])
    assert rc == 0

    assert (saida / "2019" / "Tema_09_Seguranca_20260615.xls").read_bytes() == b"seg19"
    assert not (saida / "2019" / "Tema_09_Seguranca_20220512.xls").exists()  # pega a mais recente
    assert not (saida / "2019" / "Tema_03_Alimentacao_20260615.xls").exists()  # fora do escopo
    assert (saida / "2024" / "Tema_09_Seguranca_XLSX_20260525" / "tabela_9.1.xlsx").exists()

    m = _manifesto(saida)
    assert set(m) == {("2019", "guia"), ("2019", "tema_09"), ("2024", "guia"), ("2024", "tema_09")}
    assert all(len(r["sha256"]) == 64 and r["origem_nome"] == "listagem" for r in m.values())


def test_segunda_execucao_nao_baixa_de_novo(config, tmp_path, caplog):
    saida = tmp_path / "raw"
    dl.executar(config, saida, temas=["tema_09"])
    data1 = _manifesto(saida)[("2019", "tema_09")]["baixado_em_utc"]
    caplog.clear()
    with caplog.at_level("INFO"):
        assert dl.executar(config, saida, temas=["tema_09"]) == 0
    assert "já existe" in caplog.text
    assert _manifesto(saida)[("2019", "tema_09")]["baixado_em_utc"] == data1


def test_arquivo_ausente_gera_erro_sem_derrubar_o_resto(config, tmp_path):
    saida = tmp_path / "raw"
    # tema_02 e tema_17 não existem no servidor de teste
    rc = dl.executar(config, saida, edicoes=["2019"], temas=["tema_02", "tema_09"])
    assert rc == 1
    assert (saida / "2019" / "Tema_09_Seguranca_20260615.xls").exists()
    assert not list((saida / "2019").glob("*.part"))


def test_zip_com_caminho_perigoso_e_bloqueado(tmp_path):
    z = tmp_path / "ruim.zip"
    with zipfile.ZipFile(z, "w") as f:
        f.writestr("../../fora.txt", b"x")
    with pytest.raises(IOError):
        dl.extrair_zip(z)
    assert not (tmp_path.parent / "fora.txt").exists()


def test_config_real_tem_fallback_que_bate_com_o_padrao():
    import re
    cfg = yaml.safe_load((RAIZ / "config" / "fontes.yaml").read_text(encoding="utf-8"))
    for ed in cfg["edicoes"].values():
        for t in ed["temas"].values():
            assert re.match(t["padrao"], t["fallback"]), t["fallback"]
