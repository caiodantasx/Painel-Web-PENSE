"""Gera dist/dashboard/: versão do painel pronta para publicar (GitHub Pages, Netlify, etc.).

* copia index.html com CSS e JS embutidos (um único arquivo de página);
* copia os dados gerados pela pipeline (pense_bundle.json e a base aprovada em CSV);
* copia a malha das UFs.

Uso:  python scripts/build_dashboard.py [--fragment]
  --fragment  gera a página sem <!doctype>/<html>/<head>/<body> (formato exigido por
              alguns hospedeiros que envolvem a página automaticamente).
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
SRC = ROOT / "dashboard"
OUT = ROOT / "dist" / "dashboard"


def build(fragment: bool = False) -> Path:
    html = (SRC / "index.html").read_text(encoding="utf-8")
    css = (SRC / "assets" / "app.css").read_text(encoding="utf-8")
    js = (SRC / "assets" / "app.js").read_text(encoding="utf-8")
    html = html.replace('<link rel="stylesheet" href="assets/app.css">', f"<style>\n{css}\n</style>")
    html = html.replace('<script src="assets/app.js"></script>', f"<script>\n{js}\n</script>")
    if fragment:
        # Em hospedeiros com sandbox, links de download não funcionam: remove o link direto.
        html = re.sub(r"<!-- download-base -->.*?<!-- /download-base -->", "", html, flags=re.S)
        html = re.sub(r"<!doctype html>\s*|<html[^>]*>\s*|</html>\s*|<head>\s*|</head>\s*|<body>\s*|</body>\s*", "", html, flags=re.I)
        html = re.sub(r'<meta charset="utf-8">\s*|<meta name="viewport"[^>]*>\s*', "", html)
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "data").mkdir(parents=True)
    (OUT / "assets" / "geo").mkdir(parents=True)
    (OUT / "index.html").write_text(html, encoding="utf-8")
    bundle = SRC / "data" / "pense_bundle.json"
    if not bundle.exists():
        sys.exit("dashboard/data/pense_bundle.json não existe: rode antes python scripts/run_pipeline.py")
    shutil.copy(bundle, OUT / "data" / "pense_bundle.json")
    approved = ROOT / "data" / "curated" / "pense_observations_approved.csv"
    if approved.exists():
        _slim_csv(approved, OUT / "data" / "pense_base_aprovada.csv")
    for geo in ("br_uf.json", "capitais.json"):
        shutil.copy(SRC / "assets" / "geo" / geo, OUT / "assets" / "geo" / geo)
    print(f"Painel gerado em {OUT}")
    return OUT


from pense.exports.writers import SLIM_FIELDS  # noqa: E402


def _slim_csv(src: Path, dst: Path) -> None:
    """Versão enxuta da base aprovada (sem textos longos repetidos) para download no painel."""
    import csv
    with src.open(encoding="utf-8-sig", newline="") as fi, dst.open("w", encoding="utf-8-sig", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=SLIM_FIELDS, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for row in csv.DictReader(fi):
            w.writerow(row)


if __name__ == "__main__":
    build("--fragment" in sys.argv)
