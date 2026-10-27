"""Testes ponta a ponta do painel (RNF03 acessibilidade, RNF04 responsividade).

Usam Playwright + Chromium; são pulados se não estiverem instalados
(``pip install playwright && playwright install chromium``).
"""
import functools
import http.server
import json
import threading
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
pw = pytest.importorskip("playwright.sync_api")


@pytest.fixture(scope="module")
def server():
    if not (ROOT / "dashboard" / "data" / "pense_bundle.json").exists():
        pytest.skip("rode a pipeline antes (dashboard/data/pense_bundle.json ausente)")
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT / "dashboard"))
    handler.log_message = lambda *a, **k: None
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()


@pytest.fixture(scope="module")
def browser():
    with pw.sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception as exc:  # navegador não instalado
            pytest.skip(f"Chromium indisponível: {exc}")
        yield b
        b.close()


def _open(browser, url, **ctx):
    page = browser.new_page(**ctx)
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.route("**/fonts.googleapis.com/**", lambda r: r.abort())
    page.goto(url, wait_until="networkidle")
    page.wait_for_selector("#chart-categories svg")
    return page, errors


def test_all_pages_render_without_script_errors(server, browser):
    page, errors = _open(browser, server)
    for tab in ["territory", "history", "quality", "about", "overview"]:
        page.click(f"#tab-{tab}")
        page.wait_for_timeout(150)
        assert page.is_visible(f"#page-{tab}")
    assert errors == []


def test_values_shown_come_from_bundle(server, browser):
    page, _ = _open(browser, server)
    bundle = json.loads((ROOT / "dashboard" / "data" / "pense_bundle.json").read_text(encoding="utf-8"))
    hero = page.inner_text("#tile-headline .value").replace("%", "").replace(",", ".").strip()
    known = {round(e, 1) for e in bundle["obs"]["e"] if e is not None}
    assert float(hero) in known


def test_unavailable_combinations_are_disabled(server, browser):
    page, _ = _open(browser, server)
    page.select_option("#f-indicator", "PENSE_2024__17.1")
    disabled = page.eval_on_selector_all("#f-sex option", "os => os.filter(o => o.disabled).map(o => o.value)")
    assert set(disabled) == {"Homem", "Mulher"}, "17.1 não publica recorte por sexo"


def test_keyboard_navigation_and_labels(server, browser):
    page, _ = _open(browser, server)
    unlabeled = page.eval_on_selector_all("select", "ss => ss.filter(s => !document.querySelector(`label[for='${s.id}']`)).length")
    assert unlabeled == 0
    page.focus("#tab-territory")
    page.keyboard.press("Enter")
    page.wait_for_timeout(150)
    assert page.is_visible("#page-territory")
    page.focus("#chart-ranking g.row")
    assert page.is_visible("#tooltip"), "tooltip também deve abrir por foco"


def test_mobile_360_has_no_horizontal_scroll(server, browser):
    page, errors = _open(browser, server, viewport={"width": 360, "height": 780})
    for tab in ["overview", "territory", "quality"]:
        page.click(f"#tab-{tab}")
        page.wait_for_timeout(150)
        sw, iw = page.evaluate("[document.documentElement.scrollWidth, window.innerWidth]")
        assert sw <= iw, f"rolagem horizontal na página {tab}: {sw} > {iw}"
    assert errors == []


def test_map_is_first_thing_on_overview(server, browser):
    """Pedido do usuário: o mapa do Brasil é o primeiro conteúdo da primeira página."""
    page, errors = _open(browser, server, viewport={"width": 1366, "height": 768})
    page.wait_for_selector("#map svg path")
    box = page.eval_on_selector("#map svg", "e => e.getBoundingClientRect().toJSON()")
    first = page.evaluate("""() => [...document.querySelectorAll('#page-overview .panel')]
        .filter(e => e.offsetParent).sort((a, b) => a.getBoundingClientRect().top - b.getBoundingClientRect().top
        || a.getBoundingClientRect().left - b.getBoundingClientRect().left)[0].classList.contains('map-panel')""")
    assert first, "o primeiro painel da Visão geral deve ser o do mapa"
    assert box["top"] < 768 and box["height"] > 250, "mapa visível na primeira tela"
    assert errors == []


def test_map_click_selects_and_scope_switch_respects_availability(server, browser):
    page, _ = _open(browser, server)
    page.wait_for_selector("#map svg path[tabindex='0']")
    page.click("#map svg path[tabindex='0']")
    page.wait_for_timeout(120)
    assert page.is_visible("#tile-selected .value"), "clicar numa UF abre a comparação"
    assert page.locator("#rank-table tr.sel").count() == 1, "a mesma UF fica destacada no ranking"
    # 2009 só publica capitais: UF e Regiões ficam desativados e o mapa usa marcadores
    page.select_option("#f-edition", "PENSE_2009")
    page.wait_for_timeout(150)
    states = page.eval_on_selector_all(".scope-switch[data-switch=map] .seg", "bs => bs.map(b => [b.textContent, b.disabled])")
    assert dict(states)["Capitais"] is False and dict(states)["Estados (UF)"] is True
    assert page.locator("#map svg circle").count() > 0


def test_history_page_shows_harmonized_microdata_series(server, browser):
    bundle = json.loads((ROOT / "dashboard" / "data" / "pense_bundle.json").read_text(encoding="utf-8"))
    if "micro" not in bundle:
        pytest.skip("estimativas dos microdados não geradas")
    page, errors = _open(browser, server)
    page.click("#tab-history")
    page.wait_for_selector("#table-micro-overview tbody tr")
    n13 = sum(1 for i in bundle["micro"]["indicators"] if i.get("population") != "9ANO")
    assert page.locator("#table-micro-overview tbody tr").count() == n13
    assert page.locator("#chart-micro svg circle").count() >= 2
    assert "microdados" in page.inner_text("#micro-overview-legend").lower(), "origem do dado sempre explícita"
    page.select_option("#f-micro-indicator", "ESCOLA_LOCAL_DROGAS")
    page.wait_for_timeout(150)
    assert page.locator("#chart-micro path.series-line").count() == 0, "pendente de revisão: sem linha de tendência"
    assert errors == []


def test_official_9th_grade_series_marks_origin_of_each_point(server, browser):
    bundle = json.loads((ROOT / "dashboard" / "data" / "pense_bundle.json").read_text(encoding="utf-8"))
    if "official" not in bundle.get("micro", {}):
        pytest.skip("série oficial não carregada")
    page, errors = _open(browser, server)
    page.click("#tab-history")
    page.wait_for_selector("#table-official tbody tr")
    assert page.locator("#table-official tbody tr").count() == len(bundle["micro"]["official"]["tables"])
    page.select_option("#f-off-table", "6")  # 10.7, trajeto inseguro: 2009–2019 publicados (+ 2024 se estiver na série)
    page.wait_for_timeout(120)
    t = bundle["micro"]["official"]["tables"][6]
    n_pub = len([y for y in t["years"] if y != 2024])
    if t["extension_2024"]:
        assert page.locator("#chart-official circle.pt-micro").count() == 1, "só 2024 é calculado"
        assert page.locator("#chart-official circle").count() == n_pub + 1
    else:   # 2024 fora da série por decisão registrada (D29): nenhum ponto calculado, nota diz o motivo
        assert page.locator("#chart-official circle.pt-micro").count() == 0
        assert page.locator("#chart-official circle").count() == n_pub
        assert "decisão registrada" in t["extension_note"] and "não reproduzida" not in t["extension_note"]
        assert "decisão registrada" in page.inner_text("#official-legend")
    assert errors == []


def test_no_confirmed_change_without_researcher_decision(server, browser):
    """Sem decisão registrada em comparability_decisions.csv, nenhum lugar do painel mostra o selo
    'Diferença significativa a 5%' (D27; antes 'Mudança confirmada', que também não pode aparecer)."""
    bundle = json.loads((ROOT / "dashboard" / "data" / "pense_bundle.json").read_text(encoding="utf-8"))
    if "micro" not in bundle:
        pytest.skip("estimativas dos microdados não geradas")
    decided = [i["key"] for i in bundle["micro"]["indicators"] if i["comparability"]["decision_status"] == "DECISAO_REGISTRADA"]
    page, errors = _open(browser, server)
    page.click("#tab-history")
    page.wait_for_selector("#table-micro-overview tbody tr")
    chips = lambda: page.eval_on_selector_all("#page-history .chip", "cs => cs.map(c => c.textContent.trim())")  # noqa: E731
    assert "Mudança confirmada" not in chips(), "rótulo antigo"
    assert "proposta automática" in page.inner_text("#table-micro-overview").lower(), "há indicadores sem decisão"
    # indicadores SEM decisão que têm ao menos uma diferença significativa (escolhidos pelos dados, não por nome fixo)
    sig_keys = {k.split("|")[0] for k, d in bundle["micro"].get("diffs", {}).items() if d[4]}
    undecided = [i["key"] for i in bundle["micro"]["indicators"] if i["key"] not in decided and i["key"] in sig_keys]
    if not undecided:
        pytest.skip("nenhum indicador sem decisão com diferença significativa (regra coberta em test_rotulo_significancia)")
    for key in undecided:   # sem decisão registrada, nunca há o selo, mesmo com diferença significativa
        page.select_option("#f-micro-indicator", key)
        page.wait_for_timeout(120)
        detail = page.eval_on_selector_all("#micro-detail .chip", "cs => cs.map(c => c.textContent.trim())")
        assert "Diferença significativa a 5%" not in detail and "Mudança confirmada" not in detail, key
    page.select_option("#f-micro-indicator", "CAPACETE_AS_VEZES_OU_MAIS")
    page.wait_for_timeout(150)
    assert page.locator("#chart-micro path.series-line").count() == 0, "fora da série: sem linha de tendência"
    assert "experimental" in page.inner_text("#official-legend").lower()
    assert errors == []


def test_every_number_says_what_it_is_a_percentage_of(server, browser):
    """Mapa, número principal e definição dizem 'X% dos escolares…', a base e quem respondeu."""
    page, errors = _open(browser, server)
    assert "dos escolares" in page.inner_text("#map-reading")
    head = page.inner_text("#tile-headline")
    assert "em cada 100 escolares" in head and "Os 100% são" in head and "Quem respondeu" in head
    assert "ocorrências" in head and "boletim de ocorrência" in head, "diz explicitamente o que o número NÃO é"
    d = page.inner_text("#definition")
    assert "como ler" in d.lower() and "Os 100% são" in d and "Quem respondeu" in d
    assert "valores em % dos escolares" in page.inner_text("#tile-extremes"), "lista de destaques diz a unidade"
    assert errors == []


def test_edition_switch_lists_single_year_editions_only(server, browser):
    bundle = json.loads((ROOT / "dashboard" / "data" / "pense_bundle.json").read_text(encoding="utf-8"))
    single = {m["edition_id"] for m in bundle["measures"] if not m["multi_year"]}
    page, errors = _open(browser, server)
    assert page.locator("#edition-switch .es-btn").count() == len(single)
    labels = page.eval_on_selector_all("#f-edition option", "os => os.map(o => o.textContent)")
    assert len(labels) == len(set(labels)) == len(single), "rótulos de edição únicos, sem a série multianual"
    page.locator("#edition-switch .es-btn").nth(1).click()
    page.wait_for_timeout(200)
    assert page.locator("#edition-switch .es-btn.on").count() == 1 and errors == []
