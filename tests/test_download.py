"""
Testes do 01_download.py.

Em vez de usar o site do IBGE (que pode estar fora do ar), os testes criam
um "IBGE falso" no próprio computador, com arquivos de mentira com os mesmos
nomes, e conferem se o script se comporta certo.

Rodar:  pytest -q
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

# Carrega o script (o nome começa com número, então não dá para usar "import")
PROJETO = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("download", PROJETO / "src" / "01_download.py")
download = importlib.util.module_from_spec(spec)
sys.modules["download"] = download
spec.loader.exec_module(download)


@pytest.fixture()
def ibge_falso(tmp_path):
    """Sobe um site local que imita as pastas do IBGE e devolve as FONTES apontando para ele."""
    site = tmp_path / "site"
    p2019 = site / "2019"
    p2024 = site / "2024"
    p2019.mkdir(parents=True)
    p2024.mkdir(parents=True)

    (p2019 / "Guia_Tabelas_PeNSE_2019_20260615.xls").write_bytes(b"guia 2019")
    (p2019 / "Tema_09_Seguranca_20220512.xls").write_bytes(b"versao antiga")
    (p2019 / "Tema_09_Seguranca_20260615.xls").write_bytes(b"versao nova")
    (p2019 / "Tema_03_Alimentacao_20260615.xls").write_bytes(b"fora do tema")

    zip_em_memoria = io.BytesIO()
    with zipfile.ZipFile(zip_em_memoria, "w") as z:
        z.writestr("tabela_9.1.xlsx", b"conteudo")
    (p2024 / "Tema_09_Seguranca_XLSX_20260525.zip").write_bytes(zip_em_memoria.getvalue())

    servidor = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(site)))
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    endereco = f"http://127.0.0.1:{servidor.server_address[1]}"

    fontes = {
        "2019": {"pasta": f"{endereco}/2019/", "temas": {
            "guia":    download.FONTES["2019"]["temas"]["guia"],
            "tema_09": download.FONTES["2019"]["temas"]["tema_09"],
        }},
        "2024": {"pasta": f"{endereco}/2024/", "temas": {
            "tema_09": download.FONTES["2024"]["temas"]["tema_09"],
        }},
    }
    yield fontes
    servidor.shutdown()


def ler_manifesto(pasta):
    with open(pasta / "manifesto.csv", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_baixa_os_arquivos_certos(ibge_falso, tmp_path):
    saida = tmp_path / "raw"
    assert download.main(ibge_falso, saida) == 0

    # pegou a versão mais nova e ignorou a antiga
    assert (saida / "2019" / "Tema_09_Seguranca_20260615.xls").read_bytes() == b"versao nova"
    assert not (saida / "2019" / "Tema_09_Seguranca_20220512.xls").exists()
    # não baixou tema que não pedimos
    assert not (saida / "2019" / "Tema_03_Alimentacao_20260615.xls").exists()
    # descompactou o zip de 2024
    assert (saida / "2024" / "Tema_09_Seguranca_XLSX_20260525" / "tabela_9.1.xlsx").exists()


def test_manifesto_registra_tudo(ibge_falso, tmp_path):
    saida = tmp_path / "raw"
    download.main(ibge_falso, saida)
    linhas = ler_manifesto(saida)
    assert len(linhas) == 3
    assert all(len(l["sha256"]) == 64 for l in linhas)


def test_nao_baixa_de_novo(ibge_falso, tmp_path, capsys):
    saida = tmp_path / "raw"
    download.main(ibge_falso, saida)
    download.main(ibge_falso, saida)
    assert "já existe, pulando" in capsys.readouterr().out


def test_um_erro_nao_para_os_outros(ibge_falso, tmp_path):
    saida = tmp_path / "raw"
    ibge_falso["2019"]["temas"]["tema_17"] = download.FONTES["2019"]["temas"]["tema_17"]  # não existe no site falso
    assert download.main(ibge_falso, saida) == 1
    assert (saida / "2019" / "Tema_09_Seguranca_20260615.xls").exists()


def test_nomes_conferidos_batem_com_o_comeco():
    for config in download.FONTES.values():
        for comeco, nome_conferido in config["temas"].values():
            assert nome_conferido.startswith(comeco)
