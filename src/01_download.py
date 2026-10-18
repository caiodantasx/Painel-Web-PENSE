"""
01_download.py - Baixa as tabelas oficiais da PeNSE (IBGE) usadas no painel.

Etapa 1 do pipeline do PeNSE em Painel:
    01_download.py  -> data/raw/        (arquivos originais do IBGE, intocados)
    02_...          -> data/interim/    (próximas etapas)

O que o script faz:
  1. Lê config/fontes.yaml (edições, diretórios do IBGE e temas).
  2. Lista o diretório do IBGE e localiza cada tema pelo padrão do nome.
  3. Baixa os arquivos que ainda não existem em data/raw/<edição>/.
  4. Descompacta os .zip (2024) numa pasta ao lado.
  5. Grava data/raw/manifesto.csv com URL, tamanho, SHA-256 e data,
     garantindo a rastreabilidade de cada número às tabelas oficiais.

Uso:
    python src/01_download.py                    # tudo
    python src/01_download.py --edicoes 2024     # só uma edição
    python src/01_download.py --temas tema_09    # só um tema
    python src/01_download.py --dry-run          # mostra o que faria
    python src/01_download.py --force            # baixa de novo
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import logging
import re
import sys
import time
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, unquote

import requests
import yaml

RAIZ = Path(__file__).resolve().parents[1]
CONFIG_PADRAO = RAIZ / "config" / "fontes.yaml"
SAIDA_PADRAO = RAIZ / "data" / "raw"

TIMEOUT = 60  # segundos
TENTATIVAS = 4
USER_AGENT = "pense-em-painel/0.1 (TCC; dados abertos IBGE)"

log = logging.getLogger("download")


@dataclass
class Item:
    edicao: str
    tema: str
    descricao: str
    url: str
    arquivo: str
    origem_nome: str  # "listagem" ou "fallback"


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #
def nova_sessao() -> requests.Session:
    s = requests.Session()
    s.headers["User-Agent"] = USER_AGENT
    return s


def get_com_retry(sessao: requests.Session, url: str, **kw) -> requests.Response:
    """GET com novas tentativas e espera crescente (o FTP do IBGE oscila)."""
    ultimo_erro: Exception | None = None
    for tentativa in range(1, TENTATIVAS + 1):
        try:
            r = sessao.get(url, timeout=TIMEOUT, **kw)
            if r.status_code in (429, 500, 502, 503, 504):
                raise requests.HTTPError(f"HTTP {r.status_code}", response=r)
            r.raise_for_status()
            return r
        except requests.RequestException as e:
            ultimo_erro = e
            # 404 e afins não melhoram tentando de novo
            resp = getattr(e, "response", None)
            if resp is not None and 400 <= resp.status_code < 500 and resp.status_code != 429:
                break
            if tentativa < TENTATIVAS:
                espera = 2 ** tentativa
                log.warning("  falhou (%s); nova tentativa em %ss", e, espera)
                time.sleep(espera)
    assert ultimo_erro is not None
    raise ultimo_erro


# --------------------------------------------------------------------------- #
# Localização dos arquivos
# --------------------------------------------------------------------------- #
HREF_RE = re.compile(r'href="([^"?#]+)"', re.IGNORECASE)


def listar_diretorio(sessao: requests.Session, base_url: str) -> list[str]:
    """Nomes de arquivo de uma listagem de diretório do servidor do IBGE."""
    html = get_com_retry(sessao, base_url).text
    nomes = []
    for href in HREF_RE.findall(html):
        nome = unquote(href.rstrip("/").split("/")[-1])
        if nome and not href.endswith("/"):
            nomes.append(nome)
    return nomes


def escolher(nomes: list[str], padrao: str) -> str | None:
    """Se houver mais de uma versão, fica com a de data mais recente no nome."""
    regex = re.compile(padrao)
    candidatos = sorted(n for n in nomes if regex.match(n))
    return candidatos[-1] if candidatos else None


def resolver_itens(sessao, config: dict, edicoes, temas) -> list[Item]:
    itens: list[Item] = []
    for edicao, cfg in config["edicoes"].items():
        if edicoes and edicao not in edicoes:
            continue
        base = cfg["base_url"]
        try:
            nomes = listar_diretorio(sessao, base)
            log.info("[%s] %d arquivos na listagem de %s", edicao, len(nomes), base)
        except requests.RequestException as e:
            log.warning("[%s] não consegui ler a listagem (%s); usando nomes de fallback", edicao, e)
            nomes = []

        for tema, tcfg in cfg["temas"].items():
            if temas and tema not in temas:
                continue
            arquivo = escolher(nomes, tcfg["padrao"]) if nomes else None
            origem = "listagem"
            if arquivo is None:
                if nomes:
                    log.warning("[%s] %s não encontrado na listagem; tentando fallback", edicao, tema)
                arquivo, origem = tcfg["fallback"], "fallback"
            itens.append(Item(edicao, tema, tcfg["descricao"], urljoin(base, arquivo), arquivo, origem))
    return itens


# --------------------------------------------------------------------------- #
# Download, verificação e extração
# --------------------------------------------------------------------------- #
def sha256(caminho: Path) -> str:
    h = hashlib.sha256()
    with caminho.open("rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def baixar(sessao, url: str, destino: Path) -> None:
    """Baixa para um .part e só renomeia no fim: nunca deixa arquivo pela metade."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    tmp = destino.with_name(destino.name + ".part")
    r = get_com_retry(sessao, url, stream=True)
    esperado = int(r.headers.get("Content-Length", 0))
    with tmp.open("wb") as f:
        for bloco in r.iter_content(1 << 16):
            f.write(bloco)
    recebido = tmp.stat().st_size
    if esperado and recebido != esperado:
        tmp.unlink(missing_ok=True)
        raise IOError(f"download incompleto: {recebido} de {esperado} bytes")
    if recebido == 0:
        tmp.unlink(missing_ok=True)
        raise IOError("arquivo vazio")
    tmp.replace(destino)


def extrair_zip(caminho: Path) -> int:
    """Extrai o zip em <pasta>/<nome sem .zip>/, bloqueando caminhos perigosos."""
    pasta = caminho.with_suffix("")
    pasta.mkdir(exist_ok=True)
    raiz = pasta.resolve()
    n = 0
    with zipfile.ZipFile(caminho) as z:
        for membro in z.infolist():
            alvo = (pasta / membro.filename).resolve()
            if raiz not in alvo.parents and alvo != raiz:
                raise IOError(f"caminho suspeito no zip: {membro.filename}")
            if membro.is_dir():
                continue
            alvo.parent.mkdir(parents=True, exist_ok=True)
            with z.open(membro) as src, alvo.open("wb") as dst:
                dst.write(src.read())
            n += 1
    return n


# --------------------------------------------------------------------------- #
# Manifesto
# --------------------------------------------------------------------------- #
CAMPOS = ["edicao", "tema", "descricao", "arquivo", "url", "origem_nome",
          "tamanho_bytes", "sha256", "baixado_em_utc"]


def ler_manifesto(caminho: Path) -> dict[tuple[str, str], dict]:
    if not caminho.exists():
        return {}
    with caminho.open(encoding="utf-8", newline="") as f:
        return {(r["edicao"], r["tema"]): r for r in csv.DictReader(f)}


def gravar_manifesto(caminho: Path, linhas: dict[tuple[str, str], dict]) -> None:
    with caminho.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        w.writeheader()
        for chave in sorted(linhas):
            w.writerow(linhas[chave])


# --------------------------------------------------------------------------- #
# Principal
# --------------------------------------------------------------------------- #
def executar(config_path: Path, saida: Path, edicoes=None, temas=None,
             force=False, dry_run=False) -> int:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    sessao = nova_sessao()
    itens = resolver_itens(sessao, config, edicoes, temas)
    if not itens:
        log.error("Nenhum item selecionado. Confira --edicoes/--temas e o fontes.yaml.")
        return 2

    manifesto_path = saida / "manifesto.csv"
    manifesto = ler_manifesto(manifesto_path)
    falhas = 0

    for it in itens:
        destino = saida / it.edicao / it.arquivo
        rotulo = f"[{it.edicao}] {it.tema:<8} {it.arquivo}"
        if dry_run:
            log.info("%s  <- %s (%s)", rotulo, it.url, it.origem_nome)
            continue
        try:
            if destino.exists() and not force:
                log.info("%s  já existe, pulando", rotulo)
            else:
                log.info("%s  baixando...", rotulo)
                baixar(sessao, it.url, destino)
            if destino.suffix.lower() == ".zip":
                n = extrair_zip(destino)
                log.info("%s  %d arquivo(s) extraído(s)", " " * len(rotulo), n)

            # mantém a data original se o arquivo não foi baixado de novo
            anterior = manifesto.get((it.edicao, it.tema), {})
            data = anterior.get("baixado_em_utc")
            if force or anterior.get("arquivo") != it.arquivo or not data:
                data = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            manifesto[(it.edicao, it.tema)] = {
                "edicao": it.edicao, "tema": it.tema, "descricao": it.descricao,
                "arquivo": it.arquivo, "url": it.url, "origem_nome": it.origem_nome,
                "tamanho_bytes": destino.stat().st_size, "sha256": sha256(destino),
                "baixado_em_utc": data,
            }
        except Exception as e:  # segue com os demais e informa no fim
            falhas += 1
            log.error("%s  ERRO: %s", rotulo, e)

    if dry_run:
        return 0
    saida.mkdir(parents=True, exist_ok=True)
    gravar_manifesto(manifesto_path, manifesto)
    log.info("Manifesto: %s", manifesto_path)
    if falhas:
        log.error("%d arquivo(s) com erro. Rode de novo: o que já baixou é mantido.", falhas)
        return 1
    log.info("Concluído: %d arquivo(s) ok.", len(itens))
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Baixa as tabelas oficiais da PeNSE (IBGE).")
    p.add_argument("--edicoes", nargs="+", help="ex.: 2019 2024 (padrão: todas)")
    p.add_argument("--temas", nargs="+", help="ex.: tema_09 guia (padrão: todos)")
    p.add_argument("--force", action="store_true", help="baixa de novo mesmo se já existir")
    p.add_argument("--dry-run", action="store_true", help="só mostra o que seria baixado")
    p.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    p.add_argument("--saida", type=Path, default=SAIDA_PADRAO)
    a = p.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    return executar(a.config, a.saida, a.edicoes, a.temas, a.force, a.dry_run)


if __name__ == "__main__":
    sys.exit(main())
