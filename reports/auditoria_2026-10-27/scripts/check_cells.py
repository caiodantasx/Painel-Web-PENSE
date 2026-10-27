"""Sorteia observações e relê a célula na planilha original (independente dos leitores do projeto)."""
import csv, random, sys, zipfile, io, re, collections
from pathlib import Path
import openpyxl, xlrd
P = Path(sys.argv[1]); N = int(sys.argv[2])
rows = list(csv.DictReader(open(P/"data/processed/observations_validated.csv", encoding="utf-8-sig")))
random.seed(20261027)
by_file = collections.defaultdict(list)
for r in rows: by_file[r["source_file"]].append(r)
sample = []
for f, rs in by_file.items(): sample += random.sample(rs, min(len(rs), max(3, N * len(rs) // len(rows))))
raw = {p.name: p for p in (P/"data/raw").rglob("*") if p.is_file()}
def opener(r):
    cont, name = r["source_container"], r["source_file"]
    if cont:
        zp = raw[Path(cont).name]
        member = name.split("!")[-1]; z = zipfile.ZipFile(zp); m = next(n for n in z.namelist() if n.endswith(member)); name = member
        return Path(name).name, z.read(m)
    return name, raw[Path(name).name].read_bytes()
cache = {}
def cell(r):
    nm, data = opener(r); key = (nm, r["source_sheet"])
    if key not in cache:
        if nm.lower().endswith(".xls"):
            sh = xlrd.open_workbook(file_contents=data).sheet_by_name(r["source_sheet"]); cache[key] = ("xls", sh)
        else:
            cache[key] = ("xlsx", openpyxl.load_workbook(io.BytesIO(data), data_only=True, read_only=False)[r["source_sheet"]])
    kind, sh = cache[key]
    col, row = re.match(r"([A-Z]+)(\d+)", r["source_cell"]).groups()
    c = 0
    for ch in col: c = c * 26 + ord(ch) - 64
    return sh.cell_value(int(row) - 1, c - 1) if kind == "xls" else sh.cell(int(row), c).value
ok = bad = sym = 0; probs = []
for r in sample:
    v = cell(r)
    if r["estimate"] == "":
        sym += 1; continue
    try: fv = float(str(v).replace(",", "."))
    except Exception: bad += 1; probs.append((r["source_file"], r["source_sheet"], r["source_cell"], v, r["estimate"])); continue
    if abs(fv - float(r["estimate"])) < 1e-6: ok += 1
    else: bad += 1; probs.append((r["source_file"], r["source_sheet"], r["source_cell"], v, r["estimate"]))
print(f"amostra {len(sample)} de {len(rows)} em {len(by_file)} arquivos: iguais {ok}, divergentes {bad}, sem valor numérico (símbolo) {sym}")
for p in probs[:10]: print("  ", p)
