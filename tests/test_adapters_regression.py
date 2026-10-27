"""Regressão com as tabelas reais do IBGE (dados públicos em data/raw).

Os valores esperados foram conferidos manualmente nas planilhas originais
(célula indicada em cada teste). Se um adaptador mudar e alterar a extração,
estes testes falham.
"""
import zipfile

import pytest

from pense.adapters.base import SheetContext
from pense.adapters.registry import select_adapter
from pense.ingestion.readers import read_grids
from pense.models import SourceFile
from pense.parsing.header import Vocab
from pense.parsing.title import extract_footnotes, extract_title, parse_title
from pense.standardization.normalize import join_cv
from pense.standardization.territories import TerritoryResolver


def _grids(raw_dir, archive, member, fmt):
    if archive:
        with zipfile.ZipFile(raw_dir / archive) as zf:
            data = zf.read(member)
        sid = f"{archive}!{member}"
    else:
        data = (raw_dir / member).read_bytes()
        sid = member
    src = SourceFile(sid, member, archive or "", "test", len(data), fmt)
    return {g.sheet: g for g in read_grids(src, data)}


def _extract(cfg, grid):
    title, rows = extract_title(grid)
    notes, _ = extract_footnotes(grid, max(rows) + 1)
    info = parse_title(title, notes)
    info.title_rows = rows
    ctx = SheetContext(grid, info, cfg, Vocab.from_config(cfg.vocabulary), frozenset(cfg.symbols), TerritoryResolver(cfg))
    sel = select_adapter(ctx)
    return sel, sel.adapter.extract(ctx) if sel.adapter else None


def _find(records, **kw):
    out = [r for r in records if all(r.get(k) == v for k, v in kw.items())]
    assert len(out) == 1, f"esperava 1 registro para {kw}, encontrei {len(out)}"
    return out[0]


@pytest.fixture(scope="module")
def t17_1(raw_dir):
    return _grids(raw_dir, "Tema_17_Seguranca_da_Escola_XLSX_20260525 (1).zip", "Tabelas 17.1.xlsx", "xlsx")


def test_2024_estimate_ci_and_traceability(cfg, t17_1):
    sel, out = _extract(cfg, t17_1["17.1.1"])
    assert sel.adapter.family_id == "PENSE_2024_IC"
    r = _find(out.records, territory_code="BR", age_group="Total", admin_dependency="Total",
              response_category="Assaltos e roubos a pessoas, residências e comércios")
    assert r["estimate"] == pytest.approx(28.377891926889575, abs=0)
    assert r["ci_lower"] == pytest.approx(24.66481656554449, abs=0)
    assert r["ci_upper"] == pytest.approx(32.09096728823466, abs=0)
    assert (r["source_cell"], r["ci_lower_cell"], r["ci_upper_cell"]) == ("B13", "C13", "D13")
    assert r["source_sheet"] == "17.1.1" and r["source_file"].endswith("Tabelas 17.1.xlsx")
    assert r["informant"].startswith("Escola") and r["unit"] == "%"


def test_2024_sections_map_to_dimensions(cfg, t17_1):
    _, out = _extract(cfg, t17_1["17.1.1"])
    r = _find(out.records, territory_code="N", age_group="16 e 17 anos", admin_dependency="Total",
              response_category="Tiros ou tiroteios")
    assert r["estimate"] == pytest.approx(8.036675075536879)
    priv = _find(out.records, territory_code="CO", age_group="Total", admin_dependency="Privada",
                 response_category="Violência sexual")
    assert priv["estimate"] == pytest.approx(0.1636342394191873)


def test_2024_cv_sheet_is_joined_and_consistent(cfg, t17_1):
    _, est = _extract(cfg, t17_1["17.1.1"])
    sel, cv = _extract(cfg, t17_1["17.1.1 (CV)"])
    assert sel.adapter.family_id == "PENSE_2024_CV"
    issues, compared = join_cv(est.records, cv.records)
    assert compared == len(est.records)
    assert not [i for i in issues if i.severity in ("ERROR", "REVIEW")]
    r = _find(est.records, territory_code="BR", age_group="Total", admin_dependency="Total",
              response_category="Assaltos e roubos a pessoas, residências e comércios")
    assert r["coefficient_of_variation"] == pytest.approx(6.67378963223478)


def test_2024_distribution_group_and_capitals(cfg, raw_dir):
    g = _grids(raw_dir, "Tema_17_Seguranca_da_Escola_XLSX_20260525 (1).zip", "Tabelas 17.2.xlsx", "xlsx")
    _, out = _extract(cfg, g["17.2.1"])
    head = _find(out.records, territory_code="BR", age_group="Total", admin_dependency="Total", response_category="")
    assert head["estimate"] == pytest.approx(7.693112906969835) and head["estimate_type"] == "percentual"
    once = _find(out.records, territory_code="BR", age_group="Total", admin_dependency="Total", response_category="1 vez")
    assert once["estimate_type"] == "distribuicao_percentual"
    assert once["category_group"] == "Distribuição percentual por número de vezes"
    assert once["denominator_status"] == "REGRA_DERIVADA_REVISAR"
    _, cap = _extract(cfg, g["17.2.3"])
    assert {r["territory_type"] for r in cap.records} == {"aggregate", "capital"}


def test_2009_legacy_capitals_and_continuation_sheets(cfg, raw_dir):
    g = _grids(raw_dir, "tab08avs.zip", "tab801.xls", "xls")
    sel, out = _extract(cfg, g["tab 8.1"])
    assert sel.adapter.family_id == "PENSE_2009_CAPITAIS"
    r = _find(out.records, territory_code="CAPITAIS", response_category="Trajeto casa-escola")
    assert r["estimate"] == pytest.approx(6.403346390648046) and r["source_cell"] == "B11"
    assert r["edition_year"] == 2009 and r["population_code"] == "ESCOLARES_9ANO_EF"
    dep = _find(out.records, territory_code="CAPITAIS", admin_dependency="Pública", response_category="")
    assert "CABECALHO_ASSIMETRICO" in dep["extraction_flags"]
    assert any(i.rule_id == "HDR006" for i in out.issues)
    g2 = _grids(raw_dir, "tab08avs.zip", "tab802.xls", "xls")
    _, fem = _extract(cfg, g2["tab 8.2 continuacaoA"])
    r2 = _find(fem.records, territory_code="CAPITAIS", response_category="Nenhuma")
    assert r2["sex"] == "Mulher" and r2["dimension_labels_original"] == "sex=Feminino"
    assert r2["estimate"] == pytest.approx(70.8206635301346)
    assert _find(fem.records, territory_code="5300108", response_category="Nenhuma")["territory_label_original"] == "Distrito Federal"


def test_2015_counts_percent_and_symbols(cfg, raw_dir):
    g = _grids(raw_dir, None, "Amostra_1_Tema_06_Seguranca_da_Escola.xls", "xls")
    sel, out = _extract(cfg, g["1.1.6.1"])
    assert sel.adapter.family_id == "PENSE_2015_A1"
    cnt = _find(out.records, territory_code="BR", admin_dependency="Total", unit="escolares")
    assert cnt["estimate"] == pytest.approx(1335081.040211) and cnt["estimate_type"] == "total_estimado"
    pct = _find(out.records, territory_code="BR", admin_dependency="Total", unit="%")
    assert pct["estimate"] == pytest.approx(50.79, abs=0.01)
    ro = _find(out.records, territory_code="11", admin_dependency="Privada", unit="escolares")
    assert ro["estimate"] is None and ro["estimate_symbol"] == "-" and ro["estimate_kind"] == "symbol"
    assert pct["table_family_id"] == "1.6.1" and pct["indicator_id"] == "PENSE_2015_A1__1.6.1"


def test_every_raw_sheet_gets_an_adapter(cfg, raw_dir):
    """Nenhuma aba dos arquivos reais deve ficar sem família (cobertura dos adaptadores)."""
    from pense.ingestion.discovery import discover
    res = discover(cfg)
    unmapped = []
    for item in res.items:
        for g in read_grids(item.source, item.data):
            sel, _ = _extract(cfg, g)
            if sel.adapter is None:
                unmapped.append((item.source.source_id, g.sheet, sel.reason))
    assert not unmapped, unmapped
