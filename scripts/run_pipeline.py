"""Executa a pipeline completa sem precisar instalar o pacote.

Uso:  python scripts/run_pipeline.py [-v]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pense.pipeline import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
