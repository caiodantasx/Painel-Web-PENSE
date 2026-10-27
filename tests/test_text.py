"""Normalização de textos e valores (testes unitários puros)."""
import math

import pytest

from pense.text import cell_ref, clean_text, code_from_label, col_letter, compact, parse_cell, slug

SYMBOLS = frozenset({"-", "..", "...", "x", "X"})


def test_clean_text_removes_linebreaks_nbsp_and_repeated_spaces():
    assert clean_text("Limite\ninfe-\nrior") == "Limite infe- rior"
    assert clean_text("  Brasil  ") == "Brasil"
    assert clean_text(None) == ""
    assert clean_text(float("nan")) == ""


def test_slug_and_compact_cover_accents_and_hyphenation():
    assert slug("Dependência Administrativa") == "dependencia administrativa"
    assert compact("Percen-tual") == compact("Percentual") == "percentual"
    assert compact("Limite infe- rior") == "limiteinferior"


def test_code_from_label_is_stable_ascii():
    assert code_from_label("Assaltos e roubos a pessoas, residências") == "assaltos_e_roubos_a_pessoas_residencias"


@pytest.mark.parametrize("raw,expected", [
    (12.5, 12.5), (0, 0.0), ("12,5", 12.5), ("1.234,5", 1234.5), ("12.5", 12.5), ("45%", 45.0), (" 7 ", 7.0),
])
def test_parse_cell_numbers(raw, expected):
    pv = parse_cell(raw, SYMBOLS)
    assert pv.kind == "number" and math.isclose(pv.value, expected)


def test_parse_cell_keeps_full_precision():
    v = 28.377891926889575
    assert parse_cell(v).value == v


@pytest.mark.parametrize("sym", ["-", "..", "...", "x"])
def test_parse_cell_symbols_are_not_converted_to_zero(sym):
    pv = parse_cell(sym, SYMBOLS)
    assert pv.kind == "symbol" and pv.value is None and pv.symbol == sym


@pytest.mark.parametrize("raw,kind", [
    (None, "empty"), ("", "empty"), (float("nan"), "empty"), ("#DIV/0!", "excel_error"), ("#N/A", "excel_error"),
    ("Brasil", "text"), (True, "text"),
])
def test_parse_cell_other_kinds(raw, kind):
    assert parse_cell(raw, SYMBOLS).kind == kind


def test_symbol_not_in_table_is_text_not_number():
    assert parse_cell("..", frozenset()).kind == "text"


def test_column_letters_and_refs():
    assert col_letter(0) == "A" and col_letter(25) == "Z" and col_letter(26) == "AA" and col_letter(255) == "IV"
    assert cell_ref(12, 1) == "B13"
