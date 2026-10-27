"""Apresentação do IC da diferença entre anos (D28) e rastreabilidade das evidências.

* um limite positivo ou negativo perto de zero nunca aparece como "0,0" (casas suficientes, sinal explícito);
* a frase abaixo da variação vem do mesmo indicador de significância que o selo;
* "mudança provável" não aparece mais;
* estados internos, intervalo e rótulo exibido são coerentes no pacote do painel;
* todo arquivo citado nas decisões e exclusões registradas existe no projeto.

As funções de formatação são executadas de verdade (Node.js), copiadas do próprio app.js entre os
marcadores ``fmt:start`` e ``fmt:end``. Node é opcional: sem ele, esses testes são pulados.
"""
from __future__ import annotations

import csv
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
JS = (ROOT / "dashboard" / "assets" / "app.js").read_text(encoding="utf-8")
BUNDLE = ROOT / "dashboard" / "data" / "pense_bundle.json"
SIG_STATES = {"SIGNIFICATIVA_5PCT_COM_DECISAO", "SIGNIFICATIVA_SEM_DECISAO", "SIGNIFICATIVA_APROXIMADA"}


def _fmt_source() -> str:
    m = re.search(r"// fmt:start.*?\n(.*?)// fmt:end", JS, re.S)
    assert m, "marcadores fmt:start/fmt:end ausentes em app.js"
    return m.group(1)


def _node(cases: list[list]) -> list[str]:
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js indisponível (opcional)")
    prog = _fmt_source() + f"\nconsole.log(JSON.stringify({json.dumps(cases)}.map(([lo, hi, s]) => ciDiffText(lo, hi, s))));"
    out = subprocess.run([node, "-e", prog], capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def _bounds(text: str) -> tuple[float, float]:
    m = re.search(r"de ([+−]?[\d.,]+) a ([+−]?[\d.,]+) p\.p\.", text)
    conv = lambda s: float(s.replace("−", "-").replace(".", "").replace(",", "."))  # noqa: E731
    return conv(m.group(1)), conv(m.group(2))


def test_real_case_trajeto_2019_2024():
    """Antes: 'mudança provável: de 0,0 a 1,7 p.p.'. Limite inferior real: +0,0485."""
    txt = _node([[0.0485, 1.6958, True]])[0]
    assert txt.startswith("IC 95% da diferença: de +0,05 a +1,70 p.p.")
    assert "não inclui o zero" in txt


@pytest.mark.parametrize("lo, hi, expected", [
    (-2.69, -0.10, "de −2,7 a −0,1 p.p."),
    (-0.002, 0.8, "de −0,002 a +0,800 p.p."),
    (0.0001, 0.3, "de +0,0001 a +0,3000 p.p."),   # a pipeline grava os limites com 4 casas: 0,0001 é o menor não nulo
    (0.0, 1.2, "de 0,0 a +1,2 p.p."),
    (-1.25, 3.75, "de −1,3 a +3,8 p.p."),
])
def test_bounds_keep_sign_and_same_decimals(lo, hi, expected):
    assert expected in _node([[lo, hi, False]])[0]


def test_no_nonzero_bound_shown_as_zero_grid():
    vals = [v / 10000 for v in range(-600, 601, 7) if v] + [0.05, -0.05, 0.049, -0.049, 0.0001, -0.0001]
    cases = [[v, 1.0, False] for v in vals] + [[-1.0, v, False] for v in vals]
    for (lo, hi, _), txt in zip(cases, _node(cases)):
        a, b = _bounds(txt)
        for shown, real in ((a, lo), (b, hi)):
            assert shown != 0 and (shown > 0) == (real > 0), (lo, hi, txt)


def test_sentence_follows_significance_flag():
    sig, ns = _node([[0.5, 1.0, True], [-0.5, 1.0, False]])
    assert "não inclui o zero" in sig and "inclui o zero: a amostra não permite afirmar" in ns


def test_vague_wording_removed():
    assert "mudança provável" not in JS.lower()
    assert "const ciDiffText = (" in JS and JS.count("ciDiffText(") == 2, "série harmonizada + série oficial"


def test_bundle_states_bounds_and_labels_are_coherent():
    if not BUNDLE.exists():
        pytest.skip("rode scripts/run_all.py")
    micro = json.loads(BUNDLE.read_text(encoding="utf-8")).get("micro", {})
    rows = [(d[2], d[3], d[4], d[5]) for d in micro.get("diffs", {}).values()]
    rows += [(d[2], d[3], d[4], d[6]) for d in micro.get("official", {}).get("diffs", {}).values()]
    assert rows
    labels = dict(re.findall(r'(\w+): \["([^"]+)"', re.search(r"const CHANGE_LABEL = \{(.*?)\};", JS, re.S).group(1)))
    for lo, hi, sig, status in rows:
        assert bool(sig) == (lo > 0 or hi < 0), (lo, hi, sig, status)          # significante ⇔ IC sem o zero
        assert bool(sig) == (status in SIG_STATES), (sig, status)               # estado coerente com o teste
        assert status in labels, status                                          # todo estado tem rótulo


# --------------------------------------------------------------------------- rastreabilidade
PATH_RE = re.compile(r"(?:reports|data|config|docs|scripts|src)/[\w\-./]+?\.(?:md|py|csv|toml|json)")


def _registered_rows():
    out = []
    for name in ("comparability_decisions.csv", "series_exclusions.csv"):
        p = ROOT / "config" / "microdata" / name
        if p.exists():
            with p.open(encoding="utf-8-sig", newline="") as fh:
                out += [(name, r) for r in csv.DictReader(fh) if (r.get("indicator_key") or "").strip()]
    return out


def test_every_cited_project_file_exists():
    for name, r in _registered_rows():
        for field in ("evidence_reference", "justification", "reason"):
            for path in PATH_RE.findall(r.get(field) or ""):
                assert (ROOT / path).exists(), f"{name} · {r['indicator_key']} · {field}: {path} não existe"


def test_evidence_scripts_are_in_the_project():
    base = ROOT / "reports" / "auditoria_2026-10-27"
    for f in ("sensibilidade_6ano_trajeto.md", "ic_diferenca_trajeto_2019_2024.md",
              "scripts/sensibilidade_6ano_trajeto.py", "scripts/ic_diferenca_trajeto.py"):
        assert (base / f).exists(), f
    md = (base / "sensibilidade_6ano_trajeto.md").read_text(encoding="utf-8")
    assert "2.98%" in md and "12.46 [11.26; 13.66]" in md and "-0.86 [-2.16; +0.44]" in md
    assert "/tmp/" not in md and "/home/" not in md, "sem caminho absoluto de máquina"


def test_ci_evidence_matches_pipeline_series():
    """O relatório de IC citado na decisão bate com microdata_series.csv (2019→2024, Brasil)."""
    md = (ROOT / "reports" / "auditoria_2026-10-27" / "ic_diferenca_trajeto_2019_2024.md").read_text(encoding="utf-8")
    p = ROOT / "data" / "curated" / "microdata_series.csv"
    if not p.exists():
        pytest.skip("rode scripts/run_all.py")
    with p.open(encoding="utf-8-sig", newline="") as fh:
        r = next(x for x in csv.DictReader(fh) if x["indicator_key"] == "TRAJETO_INSEGURO" and x["year"] == "2024"
                 and x["territory_code"] == "BR" and x["age_group"] == x["sex"] == x["admin_dependency"] == "Total")
    assert f"[{float(r['diff_ci_lower']):.4f}; {float(r['diff_ci_upper']):.4f}]" in md


# --------------------------------------------------------------------------- painel (opcional: playwright)
def test_dashboard_shows_sign_preserving_interval(tmp_path):
    pw = pytest.importorskip("playwright.sync_api")
    import functools
    import http.server
    import threading

    from pense.config import Config
    from pense.microdata.integrate import load_microdata_outputs
    if not BUNDLE.exists() or not (ROOT / "data" / "curated" / "microdata_estimates.csv").exists():
        pytest.skip("rode scripts/run_all.py")
    shutil.copytree(ROOT / "config", tmp_path / "config")
    (tmp_path / "data").symlink_to(ROOT / "data", target_is_directory=True)
    (tmp_path / "config" / "microdata" / "comparability_decisions.csv").write_text(
        "indicator_key,final_status,justification,evidence_reference,reviewer,decision_date\n"
        "TRAJETO_INSEGURO,COMPARABLE_WITH_CAVEATS,teste,teste,REVISOR_DE_TESTE,2026-10-27\n", encoding="utf-8")
    micro = load_microdata_outputs(Config(root=tmp_path))["bundle"]
    bundle = json.loads(BUNDLE.read_text(encoding="utf-8"))
    bundle["micro"]["diffs"], bundle["micro"]["indicators"] = micro["diffs"], micro["indicators"]
    body = json.dumps(bundle)
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT / "dashboard"))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    httpd.RequestHandlerClass.log_message = lambda *a, **k: None
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        with pw.sync_playwright() as p:
            try:
                browser = p.chromium.launch()
            except Exception as exc:  # noqa: BLE001
                pytest.skip(f"Chromium indisponível: {exc}")
            page = browser.new_page()
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.route("**/fonts.googleapis.com/**", lambda r: r.abort())
            page.route("**/data/pense_bundle.json", lambda r: r.fulfill(status=200, content_type="application/json", body=body))
            page.goto(f"http://127.0.0.1:{httpd.server_address[1]}", wait_until="networkidle")
            page.click("#tab-history")
            page.wait_for_selector("#table-micro-overview tbody tr")
            page.select_option("#f-micro-indicator", "TRAJETO_INSEGURO")
            page.wait_for_timeout(200)
            txt = page.inner_text("#micro-detail")
            assert "IC 95% da diferença: de +0,05 a +1,70 p.p. · o intervalo não inclui o zero" in txt
            assert "Diferença significativa a 5%" in txt and "mudança provável" not in txt.lower()
            assert "de 0,0 a" not in txt
            assert errors == []
            browser.close()
    finally:
        httpd.shutdown()
