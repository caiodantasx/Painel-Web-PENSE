"""Contrato dos adaptadores e motor de extração compartilhado.

Um adaptador representa uma *família estrutural* de tabelas (mesma edição,
mesma gramática de cabeçalho e de stub). Ele:

1. reconhece a família (``detect``) e devolve a evidência usada;
2. identifica cabeçalhos e semântica das colunas (via ``parsing.header``);
3. extrai valores e normaliza dimensões e territórios;
4. preserva a origem (arquivo, aba, linha, coluna, célula);
5. informa explicitamente o que não conseguiu interpretar.

As famílias diferem em detecção, metadados de edição, códigos de tabela e
ressalvas conhecidas; a leitura de cabeçalho/stub é comum para evitar código
duplicado.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..config import Config
from ..models import Issue, IssueClass, Severity, stable_id
from ..parsing.grid import Grid
from ..parsing.header import HeaderLayout, MeasureBlock, Vocab, parse_header
from ..parsing.stub import parse_stub
from ..parsing.title import PENDING, TitleInfo
from ..standardization.territories import TerritoryResolver
from ..text import code_from_label, parse_cell, slug

PROBLEM_SEVERITY = {
    "HDR001": Severity.REVIEW, "HDR002": Severity.REVIEW, "HDR003": Severity.REVIEW,
    "HDR004": Severity.REVIEW, "HDR005": Severity.INFO, "HDR006": Severity.REVIEW,
    "STB001": Severity.REVIEW, "STB002": Severity.REVIEW, "STB003": Severity.WARNING,
    "STB004": Severity.INFO, "STB005": Severity.REVIEW,
}
PROBLEM_ACTION = {
    "HDR001": "Inspecionar a coluna; se contiver dados, incluir o rótulo no vocabulário ou criar regra no adaptador.",
    "HDR002": "Verificar mesclagens do cabeçalho; pode haver colunas repetidas.",
    "HDR003": "Verificar se o bloco possui estimativa; ajustar vocabulário de medidas.",
    "HDR004": "Conferir se o limite ausente existe em outra coluna.",
    "HDR005": "Comparar caminhos de cabeçalho inferidos com a planilha original.",
    "HDR006": "Consultar a publicação/nota técnica para definir a que indicador se referem as colunas por dimensão.",
    "STB001": "Adicionar o rótulo ao vocabulário (dimensions) ou tratar no adaptador.",
    "STB002": "Conferir a linha na planilha original.",
    "STB003": "Conferir a linha na planilha original.",
    "STB004": "Nenhuma: valores da linha de seção repetem a linha seguinte e não foram extraídos.",
    "STB005": "Conferir na planilha a que território se referem os valores da linha de seção.",
}


@dataclass
class SheetContext:
    grid: Grid
    title: TitleInfo
    cfg: Config
    vocab: Vocab
    symbols: frozenset[str]
    resolver: TerritoryResolver


@dataclass
class Detection:
    score: float
    evidence: list[str] = field(default_factory=list)


@dataclass
class AdapterResult:
    records: list[dict[str, Any]] = field(default_factory=list)
    issues: list[Issue] = field(default_factory=list)
    unparsed: list[dict[str, str]] = field(default_factory=list)
    layout: HeaderLayout | None = None


class BaseAdapter:
    family_id = "BASE"
    version = "1.0"
    description = ""
    record_kind = "estimate"  # estimate | cv

    # ----------------------------------------------------- pontos de extensão
    def detect(self, ctx: SheetContext) -> Detection:  # pragma: no cover - abstrato
        raise NotImplementedError

    def edition_id(self, ctx: SheetContext) -> str:  # pragma: no cover - abstrato
        raise NotImplementedError

    def edition_for_year(self, ctx: SheetContext, year: int) -> str:
        """Edição de um valor cujo ano vem da própria coluna/linha (tabela multianual)."""
        return f"PENSE_{year}"

    def table_codes(self, table_id: str) -> tuple[str, str]:
        """(theme_id, table_family_id) a partir do código publicado."""
        parts = table_id.split(".")
        return parts[0], ".".join(parts[:2])

    # ------------------------------------------------------------- extração
    def extract(self, ctx: SheetContext) -> AdapterResult:
        res = AdapterResult()
        g, t = ctx.grid, ctx.title
        layout = parse_header(g, t.title_rows, ctx.vocab, ctx.symbols, t.statement)
        res.layout = layout
        if layout is None or not layout.blocks:
            res.unparsed.append(self._unparsed(g, "sheet", "", "Cabeçalho/blocos de medida não identificados"))
            res.issues.append(self._issue(ctx, "ADP001", Severity.REVIEW, "Aba reconhecida pela família, mas "
                                          "nenhum bloco de medida foi identificado", "",
                                          "Inspecionar a aba e ajustar o adaptador."))
            return res
        ages = (t.age_min, t.age_max) if t.age_min is not None else None
        stub = parse_stub(g, layout.body_start, layout.blocks, ctx.vocab, ctx.symbols, ages)
        structure_flags = {p[0] for p in layout.problems if p[0] == "HDR006"}
        for rule, msg, ref in layout.problems + stub.problems:
            res.issues.append(self._issue(ctx, rule, PROBLEM_SEVERITY.get(rule, Severity.REVIEW), msg, ref,
                                          PROBLEM_ACTION.get(rule, "Revisar.")))
            if rule == "HDR001":
                res.unparsed.append(self._unparsed(g, "column", ref, msg))
            if rule.startswith("STB") and rule != "STB004":
                res.unparsed.append(self._unparsed(g, "row", ref, msg))
        edition = self.edition_id(ctx)
        theme, family = self.table_codes(t.table_id)
        notes = " | ".join(t.footnotes)
        for row in stub.rows:
            if row.kind != "data":
                continue
            terr = ctx.resolver.resolve(row.label, t.territorial_scope)
            row_flags: list[str] = []
            if terr.territory is None:
                row_flags.append("TERRITORIO_NAO_RECONHECIDO")
            if row.context.get("unknown"):
                row_flags.append("SECAO_NAO_RECONHECIDA")
            for blk in layout.blocks:
                rec = self._record(ctx, row, blk, terr, edition, theme, family, notes)
                flags = list(row_flags)
                if "HDR006" in structure_flags and not blk.category_path and blk.dims:
                    flags.append("CABECALHO_ASSIMETRICO")
                if blk.dims.get("year") or row.context.get("year"):
                    flags.append("ANO_DA_CELULA")
                elif ctx.title.multi_year:
                    flags.append("ANO_INDEFINIDO")
                conflict = set(row.context) & set(blk.dims)
                if conflict:
                    flags.append("CONFLITO_DIMENSAO_LINHA_COLUNA")
                rec["extraction_flags"] = "|".join(flags)
                res.records.append(rec)
        return res

    def _record(self, ctx: SheetContext, row: Any, blk: MeasureBlock, terr: Any, edition: str,
                theme: str, family: str, notes: str) -> dict[str, Any]:
        g, t = ctx.grid, ctx.title
        r = row.row
        est = parse_cell(g.raw(r, blk.estimate_col), ctx.symbols)
        lo = parse_cell(g.raw(r, blk.ci_lower_col), ctx.symbols) if blk.ci_lower_col is not None else None
        hi = parse_cell(g.raw(r, blk.ci_upper_col), ctx.symbols) if blk.ci_upper_col is not None else None
        cv = parse_cell(g.raw(r, blk.cv_col), ctx.symbols) if blk.cv_col is not None else None
        dims = {"age_group": "Total", "sex": "Total", "admin_dependency": "Total"}
        dims.update({k: v for k, v in row.context.items() if k in dims})
        dims.update({k: v for k, v in blk.dims.items() if k in dims})
        # Ano: o da coluna/seção prevalece sobre o do título (tabelas multianuais).
        cell_year = blk.dims.get("year") or row.context.get("year")
        year = int(cell_year) if cell_year else t.year
        if cell_year:
            edition = self.edition_for_year(ctx, year)
        is_count = blk.statement_kind == "count"
        if is_count:
            est_type = "total_estimado"
        elif blk.statement_kind == "distribution" or slug(blk.category_group).startswith("distribuicao percentual"):
            est_type = "distribuicao_percentual"
        else:
            est_type = "percentual"
        denom, denom_status = self._denominator(t, blk, est_type)
        tt = terr.territory
        return {
            "observation_id": stable_id(g.source.sha256, g.sheet, r, blk.estimate_col, prefix="OBS-"),
            "record_kind": self.record_kind,
            "source_file": g.source.source_id,
            "source_container": g.source.container,
            "source_hash": g.source.sha256,
            "source_sheet": g.sheet,
            "source_row": r + 1,
            "source_column": g.ref(r, blk.estimate_col).rstrip("0123456789"),
            "source_cell": g.ref(r, blk.estimate_col),
            "ci_lower_cell": g.ref(r, blk.ci_lower_col) if blk.ci_lower_col is not None else "",
            "ci_upper_cell": g.ref(r, blk.ci_upper_col) if blk.ci_upper_col is not None else "",
            "cv_source": f"{g.sheet}!{g.ref(r, blk.cv_col)}" if blk.cv_col is not None else "",
            "adapter_family": self.family_id,
            "adapter_version": self.version,
            "edition_id": edition,
            "edition_year": year,
            "year_source": ("cabeçalho/seção da tabela" if cell_year else t.year_method),
            "edition_sample": t.sample,
            "theme_id": theme,
            "table_id": t.table_id,
            "table_family_id": family,
            "territorial_cut": t.territorial_scope,
            "indicator_id": f"{edition}__{family}",
            "indicator_name": blk.statement,
            "indicator_definition": t.statement,
            "question_text": PENDING,
            "reference_period": t.reference_period,
            "reference_period_code": t.reference_period_code,
            "population": t.population,
            "population_code": t.population_code,
            "informant": t.informant,
            "informant_method": t.informant_method,
            "denominator": denom,
            "denominator_status": denom_status,
            "territory_type": tt.type if tt else "",
            "territory_code": tt.code if tt else "",
            "territory_name": tt.name if tt else "",
            "territory_label_original": row.label,
            "uf_sigla": tt.uf_sigla if tt else "",
            "region_code": tt.region_code if tt else "",
            "territory_method": terr.method,
            **dims,
            "row_group_label": row.context_label,
            "dimension_labels_original": "; ".join(f"{k}={v}" for k, v in sorted(blk.dim_labels.items())),
            "response_category": blk.category,
            "category_code": code_from_label(blk.category) if blk.category else "geral",
            "category_group": blk.category_group,
            "unit": "escolares" if is_count else "%",
            "estimate_type": est_type,
            "estimate": est.value,
            "estimate_raw": est.raw,
            "estimate_kind": est.kind,
            "estimate_symbol": est.symbol or "",
            "ci_lower": lo.value if lo else None,
            "ci_lower_kind": lo.kind if lo else "",
            "ci_upper": hi.value if hi else None,
            "ci_upper_kind": hi.kind if hi else "",
            "confidence_level": (blk.ci_level or t.confidence_level) if blk.ci_lower_col is not None else None,
            "coefficient_of_variation": cv.value if cv else None,
            "cv_kind": cv.kind if cv else "",
            "standard_error": None,
            "standard_error_method": "",
            "multi_response": t.multi_response,
            "nonresponse_excluded": t.nonresponse_excluded,
            "methodological_note": notes,
            "header_path": blk.header_path,
        }

    @staticmethod
    def _denominator(t: TitleInfo, blk: MeasureBlock, est_type: str) -> tuple[str, str]:
        if est_type == "total_estimado":
            return "Não se aplica (contagem estimada)", "NAO_SE_APLICA"
        if t.population == PENDING:
            return PENDING, "PENDENTE"
        if est_type == "distribuicao_percentual" and blk.category_group:
            return (f"{t.population} incluídos no indicador principal da tabela (coluna Total) — "
                    f"distribuição '{blk.category_group}'", "REGRA_DERIVADA_REVISAR")
        parts = [t.population]
        if t.conditional_on:
            parts.append(f"que {t.conditional_on}")
        elif est_type == "distribuicao_percentual":
            body = t.statement
            low = body.lower()
            i = low.find(" anos que ")
            j = low.find(" por ", i + 1) if i >= 0 else -1
            if i >= 0 and j > i:
                parts.append(body[i + 6: j].strip())
        status = "EXTRAIDO_DO_TITULO"
        if t.denominator_note:
            parts.append(f"(nota: {t.denominator_note})")
        return " ".join(parts), status

    # --------------------------------------------------------------- utilit.
    def _issue(self, ctx: SheetContext, rule: str, sev: Severity, msg: str, ref: str, action: str) -> Issue:
        cls = IssueClass.NOT_VALIDATED if sev in (Severity.REVIEW,) else (
            IssueClass.CONFIRMED_ERROR if sev == Severity.ERROR else IssueClass.INFORMATIONAL)
        return Issue(rule_id=rule, severity=sev.value, issue_class=cls.value, message=msg,
                     recommended_action=action, source_file=ctx.grid.source.source_id,
                     source_sheet=ctx.grid.sheet, source_cell=ref, table_id=ctx.title.table_id,
                     stage=f"adapter:{self.family_id}")

    @staticmethod
    def _unparsed(g: Grid, kind: str, ref: str, detail: str) -> dict[str, str]:
        return {"source_file": g.source.source_id, "source_sheet": g.sheet, "kind": kind,
                "cell": ref, "detail": detail}
