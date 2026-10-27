import json, csv, sys, collections, math
P = sys.argv[1]
b = json.load(open(f"{P}/dashboard/data/pense_bundle.json", encoding="utf-8"))
rd = lambda p: list(csv.DictReader(open(f"{P}/{p}", encoding="utf-8-sig")))
O = b["obs"]; n = len(O["m"])
print("1) publicados no painel:", n, "| sem src:", sum(1 for s in O["src"] if s in (None, "", -1)), "| sem célula:", sum(1 for c in O["cell"] if not c))
print("   status:", collections.Counter(b["meta"]["status_order"][s] if isinstance(s,int) else s for s in O["st"]))
# compare with validated csv by id
val = {r["observation_id"]: r for r in rd("data/processed/observations_validated.csv")} if True else {}
miss = mism = 0
for i in range(n):
    r = val.get(O["id"][i])
    if r is None: miss += 1; continue
    e = O["e"][i]; ev = r["estimate"]
    if (e is None) != (ev in ("", None)) or (e is not None and abs(float(ev) - e) > 1e-6): mism += 1
print("   ids ausentes no CSV validado:", miss, "| estimativas divergentes:", mism)
# micro est vs microdata_estimates
M = b["micro"]; E = M["est"]; inds = M["indicators"]; eds = M["editions"]
print("2) micro.editions:", [e.get("id", e) if isinstance(e, dict) else e for e in eds])
print("   chaves de indicador:", list(inds[0].keys()))
est = rd("data/curated/microdata_estimates.csv")
idx = {(r["indicator_key"], r["edition_id"], r["territory_code"], r["age_group"], r["sex"], r["admin_dependency"]): float(r["estimate"]) for r in est if r["estimate"]}
ter = [t["code"] if isinstance(t, dict) else t for t in M["territories"]]
dims = M["dims"]
bad = notfound = 0
for i in range(len(E["k"])):
    ind = inds[E["k"][i]]; key = ind.get("key") or ind.get("k")
    ed = eds[E["ed"][i]]; ed = ed.get("id") if isinstance(ed, dict) else ed
    k = (key, ed, ter[E["t"][i]], dims["age_group"][E["a"][i]], dims["sex"][E["s"][i]], dims["admin_dependency"][E["d"][i]])
    v = idx.get(k)
    if v is None: notfound += 1
    elif E["e"][i] is not None and abs(v - E["e"][i]) > 0.051: bad += 1
print("   pontos micro:", len(E["k"]), "| sem correspondência no CSV:", notfound, "| divergentes > 0,05:", bad)
