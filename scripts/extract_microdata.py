"""Extrai os microdados da PeNSE dos ZIPs baixados do IBGE e confere tamanho e SHA-256.

Uso:  python scripts/extract_microdata.py <pasta_com_os_zips_do_ibge>

O manifesto config/microdata/source_files.csv diz, para cada edição, qual arquivo procurar
dentro dos ZIPs e para onde copiar. Os nomes dos ZIPs não importam (o IBGE e o navegador os
renomeiam): o script procura o membro em todos os ZIPs da pasta. Particularidade de 2009: o
arquivo original tem espaço no nome ('Base_Pense Completa_2009.txt') e é gravado com '_'.
Nada é sobrescrito se o arquivo já existir com o hash esperado.
"""
from __future__ import annotations

import csv
import hashlib
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(folder: str) -> int:
    with (ROOT / "config" / "microdata" / "source_files.csv").open(encoding="utf-8") as fh:
        manifest = list(csv.DictReader(fh))
    zips = sorted(Path(folder).rglob("*.zip"))
    status = 0
    for m in manifest:
        target = ROOT / m["target_path"]
        if target.exists() and sha256(target) == m["sha256"]:
            print(f"OK (já existe)  {m['edition_id']:14} {target.relative_to(ROOT)}")
            continue
        found = None
        for zp in zips:
            try:
                with zipfile.ZipFile(zp) as z:
                    for info in z.infolist():
                        if info.filename.replace("\\", "/").endswith(m["member_in_zip"].split("/")[-1]) and info.file_size == int(m["size_bytes"]):
                            found = (zp, info.filename)
                            break
            except zipfile.BadZipFile:
                continue
            if found:
                break
        if not found:
            print(f"AUSENTE         {m['edition_id']:14} procure '{m['member_in_zip']}' ({m['ibge_zip_suggested_name']})")
            status = 1
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(found[0]) as z, z.open(found[1]) as src, target.open("wb") as dst:
            shutil.copyfileobj(src, dst)
        ok = sha256(target) == m["sha256"]
        print(f"{'OK' if ok else 'HASH DIFERENTE':15} {m['edition_id']:14} {found[0].name} › {found[1]} → {target.relative_to(ROOT)}")
        status |= 0 if ok else 2
    return status


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
