"""Gera documentos derivados do código e da execução (mantém docs e sistema em sincronia).

* docs/dicionario_de_dados.md  <- standardization/schema.py
* docs/09_relatorio_testes.md  <- execução do pytest (junit XML)

Uso:  python scripts/generate_docs.py
"""
from __future__ import annotations

import datetime as dt
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pense.standardization.schema import CANONICAL_SCHEMA  # noqa: E402


def data_dictionary() -> None:
    lines = ["# Dicionário de dados — base canônica", "",
             "Gerado automaticamente de `src/pense/standardization/schema.py` por `scripts/generate_docs.py`.",
             "Uma linha da base = uma estimativa publicada (formato longo).", "",
             "| Campo | Tipo | Descrição | Origem |", "|---|---|---|---|"]
    for f, t, d, o in CANONICAL_SCHEMA:
        lines.append(f"| `{f}` | {t} | {d} | {o} |")
    lines += ["", "Valores especiais: campos não identificáveis com segurança recebem `PENDENTE`; "
              "símbolos publicados ficam em `estimate_symbol` com `estimate` vazio.", ""]
    (ROOT / "docs" / "dicionario_de_dados.md").write_text("\n".join(lines), encoding="utf-8")


def test_report() -> int:
    xml_path = ROOT / "logs" / "pytest_junit.xml"
    proc = subprocess.run([sys.executable, "-m", "pytest", "-q", f"--junitxml={xml_path}"], cwd=ROOT,
                          capture_output=True, text=True)
    root = ET.parse(xml_path).getroot()
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    by_file: dict[str, dict[str, int]] = defaultdict(lambda: {"passed": 0, "failed": 0, "skipped": 0})
    failures = []
    for case in suite.iter("testcase"):
        mod = case.get("classname", "").split(".")[-1] or (case.get("file") or case.get("name") or "").split("/")[-1].replace(".py", "")
        if not mod:
            mod = "(módulo pulado na coleta)"
        if case.find("failure") is not None or case.find("error") is not None:
            by_file[mod]["failed"] += 1
            failures.append(f"{mod}::{case.get('name')}")
        elif case.find("skipped") is not None:
            by_file[mod]["skipped"] += 1
        else:
            by_file[mod]["passed"] += 1
    total = {k: sum(v[k] for v in by_file.values()) for k in ("passed", "failed", "skipped")}
    manifest = json.loads((ROOT / "data" / "processed" / "run_manifest.json").read_text(encoding="utf-8"))
    lines = [
        "# Relatório de testes", "",
        f"Execução: {dt.datetime.now().strftime('%d/%m/%Y %H:%M')} · Python {sys.version.split()[0]} · "
        f"comando `python -m pytest` · tempo {float(suite.get('time', 0)):.1f} s", "",
        f"**Resultado: {total['passed']} aprovados, {total['failed']} falhas, {total['skipped']} pulados.**", "",
        "| Módulo de teste | Aprovados | Falhas | Pulados | O que cobre |", "|---|---|---|---|---|",
    ]
    cover = {
        "test_text": "normalização de textos e valores, símbolos, números pt-BR, erros do Excel",
        "test_apresentacao_ic": "IC da diferença no painel (D28): limite perto de zero nunca vira 0,0, frase coerente com o teste e o selo, sem 'mudança provável', arquivos citados nas decisões existem",
        "test_exclusao_edicao": "exclusão de edição da série principal por decisão registrada (D26): padrão sem exclusão, série 2019–2024 de TRAJETO_INSEGURO, sem comparação 2015→2019, dados de 2015 preservados, configuração inválida interrompe, demais indicadores intactos",
        "test_ingestion": "ZIP em memória, duplicatas por hash, zip slip, ZIP corrompido/aninhado, leitores XLSX/XLS/CSV/ODS",
        "test_parsing": "título, período, população, escopo, cabeçalho multinível por mesclagem, CSV sem mesclagem, stub, territórios",
        "test_adapters_regression": "valores reais conferidos célula a célula nas quatro famílias, junção do CV, cobertura de todas as abas",
        "test_validation": "todas as regras de qualidade, status, preservação de valores, nunca remover observações",
        "test_harmonization_historical": "comparabilidade conservadora, decisão humana com justificativa, série só para pares aprovados, média descritiva",
        "test_pipeline_integration": "pipeline ponta a ponta, falha isolada, rastreabilidade até a célula, camada aprovada, idempotência, CSV",
        "test_dashboard_e2e": "painel sem erros, mapa como primeiro painel, clique no mapa sincroniza ranking, recortes indisponíveis desativados, valores vindos da base, teclado/rótulos, 360 px sem rolagem lateral",
        "test_microdata": "estimador de desenho (fórmula fechada, domínio, pós-estratificação), diferença entre anos, regras de comparabilidade, reprodução das tabelas publicadas 2024 e 2019",
        "test_reference": "guia oficial 2024 (1.510 abas, 19 temas), questionário do aluno 2015 conferido com o PDF, conferência de abas e títulos (REF001–REF003)",
        "test_correcoes_2026_10": "adaptador 2015 A2, convenções de não resposta (abandono × sem resposta), proposta × decisão, edições sem evidência fora da série, recálculo real dos microdados contra tabelas publicadas",
        "test_multiyear": "tabelas com vários anos: ano por coluna/seção (inclusive 2009.0 do .xls), título com lista de anos, valor sem ano vai para revisão",
        "test_rotulo_significancia": "selo 'Diferença significativa a 5%' (D27): só com decisão registrada e significância, critério estatístico inalterado, estados preservados, mesmos nomes no CSV/painel/relatório, glossário sem a leitura de probabilidade",
    }
    for mod, c in sorted(by_file.items()):
        lines.append(f"| `{mod}` | {c['passed']} | {c['failed']} | {c['skipped']} | {cover.get(mod, '')} |")
    if failures:
        lines += ["", "## Falhas", ""] + [f"- `{f}`" for f in failures]
    lines += ["", "## Verificações de dados na última execução da pipeline", "",
              "| Regra | Avaliações |", "|---|---|"]
    lines += [f"| {k} | {v} |" for k, v in manifest.get("rule_checks", {}).items()]
    lines.append("")
    (ROOT / "docs" / "09_relatorio_testes.md").write_text("\n".join(lines), encoding="utf-8")
    print(proc.stdout.strip().splitlines()[-1] if proc.stdout else proc.stderr)
    return proc.returncode


if __name__ == "__main__":
    data_dictionary()
    raise SystemExit(test_report())
