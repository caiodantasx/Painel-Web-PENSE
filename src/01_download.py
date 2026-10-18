"""
ETAPA 1 - DOWNLOAD DAS TABELAS DA PeNSE

O que este script faz, em 4 passos:
  1. Entra no site do IBGE e vê quais arquivos existem.
  2. Baixa só os temas que interessam ao painel (violência e segurança).
  3. Descompacta os arquivos .zip (a edição 2024 vem zipada).
  4. Anota num "manifesto" de onde veio cada arquivo e o código SHA-256 dele,
     para provar depois que usamos os dados oficiais sem alteração.

Como rodar:
    python src/01_download.py

Resultado:
    data/raw/2019/...        arquivos de 2019
    data/raw/2024/...        arquivos de 2024
    data/raw/manifesto.csv   lista do que foi baixado
"""

import csv
import hashlib
import re
import time
import zipfile
from datetime import datetime
from pathlib import Path

import requests

# --------------------------------------------------------------------------
# CONFIGURAÇÃO: o que baixar
# --------------------------------------------------------------------------
# Para cada edição: o endereço da pasta no site do IBGE e os temas desejados.
#
# Cada tema tem:
#   - o começo do nome do arquivo (o IBGE coloca a data no final do nome,
#     ex.: Tema_09_Seguranca_20260615.xls, e troca essa data quando corrige
#     uma tabela; por isso procuramos pelo começo do nome e pegamos a versão
#     mais nova);
#   - o nome conferido em 18/10/2026, usado se a lista do site não abrir.

FONTES = {
    "2019": {
        "pasta": "https://ftp.ibge.gov.br/pense/2019/xls/",
        "temas": {
            "guia":    ("Guia_Tabelas_PeNSE_2019_",              "Guia_Tabelas_PeNSE_2019_20260615.xls"),
            "tema_02": ("Tema_02_Situacoes_em_Casa_e_na_Escola_", "Tema_02_Situacoes_em_Casa_e_na_Escola_20260615.xls"),
            "tema_09": ("Tema_09_Seguranca_",                     "Tema_09_Seguranca_20260615.xls"),
            "tema_17": ("Tema_17_Seguranca_da_Escola_",           "Tema_17_Seguranca_da_Escola_20260615.xls"),
        },
    },
    "2024": {
        "pasta": "https://ftp.ibge.gov.br/pense/2024/xlsx/",
        "temas": {
            "guia":    ("Guia_Tabelas_PeNSE_2024_",                   "Guia_Tabelas_PeNSE_2024_20260525.xlsx"),
            "tema_02": ("Tema_02_Situacoes_em_Casa_e_na_Escola_XLSX_", "Tema_02_Situacoes_em_Casa_e_na_Escola_XLSX_20260525.zip"),
            "tema_09": ("Tema_09_Seguranca_XLSX_",                     "Tema_09_Seguranca_XLSX_20260525.zip"),
            "tema_17": ("Tema_17_Seguranca_da_Escola_XLSX_",           "Tema_17_Seguranca_da_Escola_XLSX_20260525.zip"),
        },
    },
}

# O que significa cada tema (vai para o manifesto)
DESCRICAO = {
    "guia":    "Guia das tabelas (índice que explica cada tabela)",
    "tema_02": "Situações em casa e na escola (bullying, faltas por insegurança)",
    "tema_09": "Segurança (brigas, armas, agressão, violência sexual)",
    "tema_17": "Segurança da escola (respondido pela direção da escola)",
}

PASTA_DO_PROJETO = Path(__file__).resolve().parent.parent
PASTA_SAIDA = PASTA_DO_PROJETO / "data" / "raw"


# --------------------------------------------------------------------------
# PASSO 1: ver quais arquivos existem no site do IBGE
# --------------------------------------------------------------------------
def listar_arquivos(url_pasta):
    """Abre a página da pasta e devolve os nomes dos arquivos que aparecem nela."""
    html = baixar_pagina(url_pasta).text
    return re.findall(r'href="([^"/?]+\.\w+)"', html)


def escolher_arquivo(nomes, comeco):
    """Entre os arquivos que começam com `comeco`, escolhe o mais novo.
    Como a data está no fim do nome (AAAAMMDD), o maior em ordem alfabética
    é o mais recente."""
    candidatos = [n for n in nomes if n.startswith(comeco)]
    return max(candidatos) if candidatos else None


# --------------------------------------------------------------------------
# PASSO 2: baixar
# --------------------------------------------------------------------------
def baixar_pagina(url, tentativas=3):
    """Faz o download. Se o site do IBGE falhar, espera e tenta de novo."""
    for tentativa in range(1, tentativas + 1):
        try:
            resposta = requests.get(url, timeout=60)
            resposta.raise_for_status()  # dá erro se o site respondeu 404, 500...
            return resposta
        except requests.RequestException as erro:
            if tentativa == tentativas:
                raise
            print(f"    falhou ({erro}); tentando de novo em 5s...")
            time.sleep(5)


def baixar_arquivo(url, destino):
    """Baixa um arquivo e salva no destino."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    conteudo = baixar_pagina(url).content
    if not conteudo:
        raise IOError("o arquivo veio vazio")
    destino.write_bytes(conteudo)


# --------------------------------------------------------------------------
# PASSO 3: descompactar
# --------------------------------------------------------------------------
def descompactar(arquivo_zip):
    """Extrai o .zip numa pasta com o mesmo nome (sem o .zip)."""
    pasta = arquivo_zip.with_suffix("")
    with zipfile.ZipFile(arquivo_zip) as z:
        z.extractall(pasta)
        return len(z.namelist())


# --------------------------------------------------------------------------
# PASSO 4: manifesto
# --------------------------------------------------------------------------
def calcular_sha256(arquivo):
    """Gera a "impressão digital" do arquivo. Se um único byte mudar,
    o código muda. Serve para provar que o arquivo é o mesmo do IBGE."""
    return hashlib.sha256(arquivo.read_bytes()).hexdigest()


def salvar_manifesto(linhas, caminho):
    colunas = ["edicao", "tema", "descricao", "arquivo", "url", "tamanho_bytes", "sha256", "baixado_em"]
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=colunas)
        escritor.writeheader()
        escritor.writerows(linhas)


# --------------------------------------------------------------------------
# PROGRAMA PRINCIPAL
# --------------------------------------------------------------------------
def main(fontes=FONTES, pasta_saida=PASTA_SAIDA):
    manifesto = []
    erros = 0

    for edicao, config in fontes.items():
        print(f"\n=== PeNSE {edicao} ===")

        # Passo 1: lista do site (se não abrir, usa os nomes conferidos)
        try:
            nomes_no_site = listar_arquivos(config["pasta"])
        except requests.RequestException:
            print("  Não consegui abrir a lista do IBGE; usando os nomes conferidos.")
            nomes_no_site = []

        for tema, (comeco, nome_conferido) in config["temas"].items():
            nome = escolher_arquivo(nomes_no_site, comeco) or nome_conferido
            url = config["pasta"] + nome
            destino = pasta_saida / edicao / nome

            try:
                # Passo 2: baixa só se ainda não tiver baixado antes
                if destino.exists():
                    print(f"  {nome}: já existe, pulando")
                else:
                    print(f"  {nome}: baixando...")
                    baixar_arquivo(url, destino)

                # Passo 3: descompacta se for .zip
                if destino.suffix == ".zip":
                    qtd = descompactar(destino)
                    print(f"    {qtd} arquivo(s) extraído(s)")

                # Passo 4: anota no manifesto
                manifesto.append({
                    "edicao": edicao,
                    "tema": tema,
                    "descricao": DESCRICAO[tema],
                    "arquivo": nome,
                    "url": url,
                    "tamanho_bytes": destino.stat().st_size,
                    "sha256": calcular_sha256(destino),
                    "baixado_em": datetime.fromtimestamp(destino.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
                })
            except Exception as erro:
                # um arquivo com problema não impede os outros
                print(f"  ERRO em {nome}: {erro}")
                erros += 1

    pasta_saida.mkdir(parents=True, exist_ok=True)
    salvar_manifesto(manifesto, pasta_saida / "manifesto.csv")

    print(f"\nManifesto salvo em {pasta_saida / 'manifesto.csv'}")
    if erros:
        print(f"Atenção: {erros} arquivo(s) com erro. Rode o script de novo.")
        return 1
    print(f"Concluído: {len(manifesto)} arquivo(s) ok.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
