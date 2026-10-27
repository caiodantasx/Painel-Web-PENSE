"""Compara ESTRATOGEOREG × ESTRATO_EXP para 2015 A1 contra os IC da série oficial 10.x (convenção da série)."""
import sys, csv, copy, statistics as S
sys.path.insert(0, "src")
from pense.config import Config
from pense.microdata import run as R
cfg = Config(root=__import__("pathlib").Path("."))
eds, inds = R.load_config(cfg)
pub = list(csv.DictReader(open("data/processed/observations_validated.csv", encoding="utf-8-sig")))
inds = {k: v for k, v in inds.items() if "PENSE_2015_A1" in v["editions"] and k != "NONO_CINTO_FRENTE_OU_TRAS"}
for strata in ("ESTRATOGEOREG", "ESTRATO_EXP"):
    spec = copy.deepcopy(eds["PENSE_2015_A1"]); spec["strata"] = strata; spec["psu"] = [strata, "escola"]
    R.load_config = lambda c, s=spec: ({"PENSE_2015_A1": s}, inds)
    est = R.estimate_all(cfg)
    val = R.validate_against_published(est, pub)
    ci = [max(abs(float(v["diff_ci_lower_pp"] or 0)), abs(float(v["diff_ci_upper_pp"] or 0))) for v in val]
    tot = [v for v in val if v["territory_code"] == "CAPITAIS" and v["sex"] == "Total" and v["admin_dependency"] == "Total"]
    cit = [max(abs(float(v["diff_ci_lower_pp"])), abs(float(v["diff_ci_upper_pp"]))) for v in tot]
    print(f"{strata:14} recortes {len(val)}: IC ≤0,15 p.p. em {sum(c <= .15 for c in ci)/len(ci):.1%}, mediana {S.median(ci):.3f}, máx {max(ci):.2f} | "
          f"total capitais: IC máx {max(cit):.3f}")
