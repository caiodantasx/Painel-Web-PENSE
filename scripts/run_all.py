"""Executa tudo na ordem certa: pipeline → microdados (se presentes) → pipeline → painel.

A pipeline roda duas vezes porque a validação dos microdados usa as tabelas publicadas já
extraídas (1ª execução) e o pacote do painel incorpora a série dos microdados (2ª).

Uso:  python scripts/run_all.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(script: str, *args: str) -> None:
    print(f"\n=== {script} {' '.join(args)}")
    subprocess.run([sys.executable, str(ROOT / "scripts" / script), *args], check=True)


if __name__ == "__main__":
    run("run_pipeline.py")
    if any((ROOT / "data" / "microdata").glob("*/*.[cC][sS][vV]")):
        run("run_microdata.py")
        run("run_pipeline.py")
    else:
        print("Microdados ausentes em data/microdata/: série harmonizada não atualizada.")
    run("report_microdata.py")
    run("build_evidence_matrix.py")
    run("generate_docs.py")
    run("build_dashboard.py")
