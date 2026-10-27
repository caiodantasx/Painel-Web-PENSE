"""Rótulo "Diferença significativa a 5%" no lugar de "Mudança confirmada" (D27).

O que se garante:
* o selo novo só aparece com decisão de comparabilidade registrada E diferença significativa;
* sem decisão, a diferença significativa fica "aguarda decisão"; não significativa, "pode ser acaso";
* o critério estatístico não mudou (|d| > 1,96·EP da diferença);
* estados internos, CSV, pacote do painel, painel e relatório usam os mesmos nomes;
* "Mudança confirmada" / MUDANCA_CONFIRMADA não aparecem mais no código, painel, docs ou relatório;
* o glossário não traduz significância como "chance de ser acaso" ou "95% de certeza".

Responsável usado nos dados sintéticos: "REVISOR_DE_TESTE" (marcador de teste, não é decisão).
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import pytest

from pense.microdata.series import (CHANGE_NS, CHANGE_PENDING, CHANGE_SIGNIFICANT, Z95, assess_comparability,
                                    build_series, change_status)

ROOT = Path(__file__).resolve().parents[1]
CUR = ROOT / "data" / "curated"
JS = (ROOT / "dashboard" / "assets" / "app.js").read_text(encoding="utf-8")
HTML = (ROOT / "dashboard" / "index.html").read_text(encoding="utf-8")
NEW = "Diferença significativa a 5%"

EDS = {"A": {"year": 2019, "nonresponse_in_denominator": [9]}, "B": {"year": 2024, "nonresponse_in_denominator": [-9]}}
IND = {"label": "", "period": "30_DIAS", "var": "B1", "num": [1], "den": [1, 2], "editions": ["A", "B"]}
VAL = [{"edition_id": e, "indicator_key": "X", "status": "VALIDADO"} for e in "AB"]
DEC = {"indicator_key": "X", "final_status": "COMPARABLE_WITH_CAVEATS", "justification": "j", "evidence_reference": "e",
       "reviewer": "REVISOR_DE_TESTE", "decision_date": "2026-10-27"}


def _est(ed, year, e, se):
    return {"indicator_key": "X", "edition_id": ed, "edition_year": str(year), "territory_code": "BR",
            "territory_name": "Brasil", "territory_type": "country", "age_group": "Total", "sex": "Total",
            "admin_dependency": "Total", "estimate": str(e), "standard_error": str(se), "ci_lower": str(e - 1),
            "ci_upper": str(e + 1), "low_precision": "False", "nonresponse_convention": "PUBLICACAO+SERIE"}


def _last(e2, decisions, se=0.2):
    comp = assess_comparability({"X": IND}, EDS, VAL, decisions)
    return build_series([_est("A", 2019, 10.0, se), _est("B", 2024, e2, se)], comp)[-1]


# --------------------------------------------------------------------------- estados e critério
def test_internal_names():
    assert CHANGE_SIGNIFICANT == "SIGNIFICATIVA_5PCT_COM_DECISAO"
    assert CHANGE_PENDING == "SIGNIFICATIVA_SEM_DECISAO" and CHANGE_NS == "NAO_SIGNIFICATIVA"
    assert change_status(True, True) == CHANGE_SIGNIFICANT
    assert change_status(True, False) == CHANGE_PENDING
    assert change_status(False, True) == CHANGE_NS and change_status(False, False) == CHANGE_NS


def test_badge_requires_decision_and_significance():
    assert _last(11.0, [DEC])["change_status"] == CHANGE_SIGNIFICANT, "decisão + significativa → selo novo"
    assert _last(11.0, [])["change_status"] == CHANGE_PENDING, "sem decisão → aguarda decisão"
    assert _last(10.1, [DEC])["change_status"] == CHANGE_NS, "com decisão, mas não significativa → pode ser acaso"
    incomplete = dict(DEC, reviewer="")
    assert _last(11.0, [incomplete])["change_status"] == CHANGE_PENDING, "decisão incompleta não vale"
    not_comp = dict(DEC, final_status="NOT_COMPARABLE")
    comp = assess_comparability({"X": IND}, EDS, VAL, [not_comp])
    assert build_series([_est("A", 2019, 10.0, 0.2), _est("B", 2024, 11.0, 0.2)], comp) == [], \
        "decisão de não comparável: nenhum ponto de série, nenhum selo"


def test_statistical_criterion_unchanged():
    """Limite exato: |d| > 1,96·√(EP₁²+EP₂²). Com EP 0,2 nos dois anos, o limiar é ≈ 0,5544 p.p."""
    thr = Z95 * (0.2 ** 2 * 2) ** 0.5
    assert _last(10.0 + thr * 1.001, [DEC])["change_status"] == CHANGE_SIGNIFICANT
    assert _last(10.0 + thr * 0.999, [DEC])["change_status"] == CHANGE_NS
    p = _last(11.0, [DEC])
    assert p["diff_ci_lower"] > 0 and p["significant_5pct"] is True


# --------------------------------------------------------------------------- painel e textos
def _labels() -> dict[str, str]:
    block = re.search(r"const CHANGE_LABEL = \{(.*?)\};", JS, re.S).group(1)
    return dict(re.findall(r'(\w+): \["([^"]+)"', block))


def test_dashboard_labels_map_every_state():
    lab = _labels()
    assert lab[CHANGE_SIGNIFICANT] == NEW
    assert lab[CHANGE_PENDING] == "Significativa · aguarda decisão", "estado não relacionado preservado"
    assert lab[CHANGE_NS] == "Pode ser acaso da amostra", "estado não relacionado preservado"
    assert lab["SIGNIFICATIVA_APROXIMADA"] == "Significativa (teste aproximado)", "estado não relacionado preservado"
    assert f'status === "{CHANGE_SIGNIFICANT}"' in JS, "seta colorida só para o selo novo"


@pytest.mark.parametrize("path", ["dashboard/assets/app.js", "dashboard/index.html", "src/pense/microdata/series.py",
                                  "src/pense/microdata/integrate.py", "scripts/report_microdata.py",
                                  "docs/06_guia_serie_historica.md", "docs/07_manual_dashboard.md",
                                  "docs/10_pendencias.md", "README.md"])
def test_old_label_is_gone(path):
    txt = (ROOT / path).read_text(encoding="utf-8")
    assert "MUDANCA_CONFIRMADA" not in txt
    assert "mudança confirmada" not in txt.lower()
    assert "a mudança está confirmada" not in txt.lower()


def test_glossary_explains_without_probability_fallacy():
    gloss = re.search(r'significativa: "([^"]+)"', JS).group(1)
    dd = re.search(r"<dt>Diferença significativa a 5%</dt><dd>(.*?)</dd>", HTML, re.S).group(1)
    for txt in (gloss, dd):
        low = txt.lower()
        assert "intervalo de confiança de 95% da diferença" in low and "não inclui o zero" in low
        assert "não é a chance de a mudança ser real" in low
        assert "não quer dizer grande nem importante" in low and "causa" in low and "limitações" in low
        assert "menos de 5% de chance" not in low and "95% de certeza" not in low and "95% de chance" not in low
        assert "ser acaso da amostra (teste" not in low
    assert "comparável não quer dizer que houve mudança" in gloss.lower()


def test_report_source_has_no_contradictory_sentence():
    src = (ROOT / "scripts" / "report_microdata.py").read_text(encoding="utf-8")
    assert "com decisão sem decisão" not in src
    assert "o selo 'Diferença significativa a 5%' exige, além disso, decisão metodológica registrada" in src
    assert "sem decisão registrada, a diferença não recebe" in src


# --------------------------------------------------------------------------- saídas reais da pipeline
def _rows(path):
    if not path.exists():
        pytest.skip("rode scripts/run_all.py")
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def test_csv_bundle_and_dashboard_use_the_same_states():
    states = {r["change_status"] for r in _rows(CUR / "microdata_series.csv")}
    assert states <= {"", CHANGE_NS, CHANGE_PENDING, CHANGE_SIGNIFICANT}, states
    bundle = json.loads((ROOT / "dashboard" / "data" / "pense_bundle.json").read_text(encoding="utf-8"))
    micro = bundle.get("micro", {})
    used = {d[5] for d in micro.get("diffs", {}).values()} | {d[6] for d in micro.get("official", {}).get("diffs", {}).values()}
    assert "MUDANCA_CONFIRMADA" not in used
    assert used - {""} <= set(_labels()), f"estado sem rótulo no painel: {used - set(_labels())}"


def test_without_registered_decision_nothing_gets_the_badge():
    comp = {r["indicator_key"]: r for r in _rows(CUR / "microdata_comparability.csv")}
    decided = {k for k, c in comp.items() if c["decision_status"] == "DECISAO_REGISTRADA"}
    for r in _rows(CUR / "microdata_series.csv"):
        if r["change_status"] == CHANGE_SIGNIFICANT:
            assert r["indicator_key"] in decided and r["significant_5pct"].lower() == "true"
        if r["indicator_key"] not in decided:
            assert r["change_status"] != CHANGE_SIGNIFICANT


def test_generated_report_wording():
    doc = ROOT / "docs" / "12_microdados.md"
    if not doc.exists():
        pytest.skip("rode scripts/run_all.py")
    txt = doc.read_text(encoding="utf-8")
    assert "mudança confirmada" not in txt.lower()
    assert "nunca recebe o selo 'Diferença significativa a 5%'" in txt
    assert "sem decisão registrada, a diferença não recebe esse selo" in txt


# --------------------------------------------------------------------------- painel no navegador (opcional: playwright)
def test_dashboard_shows_badge_only_with_decision(tmp_path):
    """Passa pela pipeline real: decisão de teste em cópia de config/ → integração → pacote do painel
    → navegador. TRAJETO_INSEGURO (com decisão) mostra o selo; ESCOLA_INSEGURA (sem decisão) não."""
    import functools
    import http.server
    import shutil
    import threading

    from pense.config import Config
    from pense.microdata.integrate import load_microdata_outputs

    pw = pytest.importorskip("playwright.sync_api")
    bpath = ROOT / "dashboard" / "data" / "pense_bundle.json"
    if not bpath.exists() or not (CUR / "microdata_estimates.csv").exists():
        pytest.skip("rode scripts/run_all.py")
    shutil.copytree(ROOT / "config", tmp_path / "config")
    (tmp_path / "data").symlink_to(ROOT / "data", target_is_directory=True)
    with (tmp_path / "config" / "microdata" / "comparability_decisions.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["indicator_key", "final_status", "justification", "evidence_reference", "reviewer", "decision_date"])
        w.writerow(["TRAJETO_INSEGURO", "COMPARABLE_WITH_CAVEATS", "teste", "teste", "REVISOR_DE_TESTE", "2026-10-27"])
    micro = load_microdata_outputs(Config(root=tmp_path))["bundle"]
    assert micro["diffs"]["TRAJETO_INSEGURO|BR|Total|Total|Total|2024"][5] == CHANGE_SIGNIFICANT
    assert micro["diffs"]["ESCOLA_INSEGURA|BR|Total|Total|Total|2024"][5] == CHANGE_PENDING
    bundle = json.loads(bpath.read_text(encoding="utf-8"))
    bundle["micro"]["diffs"], bundle["micro"]["indicators"] = micro["diffs"], micro["indicators"]
    body = json.dumps(bundle)

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT / "dashboard"))
    handler.log_message = lambda *a, **k: None
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        with pw.sync_playwright() as p:
            try:
                browser = p.chromium.launch()
            except Exception as exc:
                pytest.skip(f"Chromium indisponível: {exc}")
            page = browser.new_page()
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.route("**/fonts.googleapis.com/**", lambda r: r.abort())
            page.route("**/data/pense_bundle.json", lambda r: r.fulfill(status=200, content_type="application/json", body=body))
            page.goto(f"http://127.0.0.1:{httpd.server_address[1]}", wait_until="networkidle")
            page.click("#tab-history")
            page.wait_for_selector("#table-micro-overview tbody tr")
            head = page.text_content("#table-micro-overview thead")   # texto do DOM (o CSS põe em maiúsculas)
            assert "Diferença significativa?" in head and "confirmada" not in head.lower()
            chips = lambda: page.eval_on_selector_all("#micro-detail .chip, #page-history .change .chip",  # noqa: E731
                                                      "cs => cs.map(c => c.textContent.trim())")
            page.select_option("#f-micro-indicator", "TRAJETO_INSEGURO")
            page.wait_for_timeout(150)
            assert NEW in chips()
            page.select_option("#f-micro-indicator", "ESCOLA_INSEGURA")
            page.wait_for_timeout(150)
            assert NEW not in chips() and "Significativa · aguarda decisão" in chips()
            assert "Mudança confirmada" not in page.inner_text("#page-history")
            assert errors == []
            browser.close()
    finally:
        httpd.shutdown()
