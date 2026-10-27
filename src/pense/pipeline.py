"""Orquestração da pipeline PeNSE.

Etapas (cada uma grava sua camada de dados):

1. ingestão ............ data/processed/inventory_files.csv
2. leitura estrutural .. data/processed/inventory_sheets.csv
3. adaptadores ......... data/staging/observations_extracted.csv   (camada "extracted")
4. normalização ........ data/processed/observations_normalized.csv (camada "normalized")
5. validação ........... data/processed/observations_validated.csv  (camada "validated")
6. harmonização ........ data/curated/indicator_catalog.csv, comparability_catalog.csv
7. série histórica ..... data/curated/historical_series*.csv
8. aprovados ........... data/curated/pense_observations_approved.csv/json (camada "approved")
9. dashboard ........... dashboard/data/pense_bundle.json

Uso: ``python -m pense.pipeline`` (ou ``python scripts/run_pipeline.py``).
A falha de um arquivo ou aba é registrada e não interrompe as demais.
"""
from __future__ import annotations

import argparse
import platform
import sys
import time
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from . import __version__
from .adapters.base import SheetContext
from .adapters.registry import select_adapter
from .config import Config
from .exports.dashboard import build_bundle, stamp_hash
from .exports.writers import SLIM_FIELDS, write_csv, write_json
from .harmonization.catalog import build_catalog
from .harmonization.comparability import evaluate, status_index
from .historical.series import build_series
from .ingestion.discovery import discover
from .ingestion.readers import ReadError, read_grids
from .logging_utils import get_logger, setup_logging
from .models import Issue, IssueClass, Severity
from .parsing.header import Vocab
from .parsing.title import extract_footnotes, extract_title, parse_title
from .reporting.reports import write_reports
from .harmonization.questions import apply_questions, build_question_map
from .microdata.integrate import load_microdata_outputs
from .validation.reference import check_against_guide
from .standardization.normalize import derive_standard_error, join_cv
from .standardization.schema import CANONICAL_FIELDS
from .standardization.territories import TerritoryResolver
from .validation.rules import ValidationSettings, Validator, assign_status

log = get_logger("pipeline")
INTERNAL_FIELDS = ["record_kind", "adapter_version", "territory_method", "estimate_kind", "ci_lower_kind",
                   "ci_upper_kind", "cv_kind"]


@dataclass
class RunResult:
    files: list[dict[str, Any]] = field(default_factory=list)
    sheets: list[dict[str, Any]] = field(default_factory=list)
    estimates: list[dict[str, Any]] = field(default_factory=list)
    cv_records: list[dict[str, Any]] = field(default_factory=list)
    issues: list[Issue] = field(default_factory=list)
    unparsed: list[dict[str, str]] = field(default_factory=list)
    catalog: list[dict[str, Any]] = field(default_factory=list)
    comparability: list[dict[str, Any]] = field(default_factory=list)
    series: list[dict[str, Any]] = field(default_factory=list)
    series_summary: list[dict[str, Any]] = field(default_factory=list)
    series_status: list[dict[str, Any]] = field(default_factory=list)
    timings: dict[str, float] = field(default_factory=dict)
    rule_checks: dict[str, int] = field(default_factory=dict)
    reference_report: list[dict[str, str]] = field(default_factory=list)
    micro: dict[str, Any] = field(default_factory=dict)


def run(cfg: Config | None = None, verbose: bool = False, write_outputs: bool = True) -> RunResult:
    cfg = cfg or Config()
    setup_logging(cfg.path("logs"), verbose)
    res = RunResult()
    t0 = time.perf_counter()
    vocab = Vocab.from_config(cfg.vocabulary)
    symbols = frozenset(cfg.symbols)
    resolver = TerritoryResolver(cfg)

    # 1) ingestão -------------------------------------------------------
    disc = discover(cfg)
    res.issues.extend(disc.issues)
    for s in disc.all_sources:
        res.files.append({"source_id": s.source_id, "file_name": s.file_name, "container": s.container,
                          "format": s.fmt, "size_bytes": s.size_bytes, "sha256": s.sha256,
                          "duplicate_of": s.duplicate_of, "status": "DUPLICADO" if s.duplicate_of else "OK"})
    res.timings["ingestion"] = time.perf_counter() - t0

    # 2-3) leitura estrutural e adaptadores -----------------------------
    t1 = time.perf_counter()
    for item in disc.items:
        try:
            grids = read_grids(item.source, item.data)
        except ReadError as exc:
            res.issues.append(Issue(rule_id="ING010", severity=Severity.ERROR.value,
                                    issue_class=IssueClass.CONFIRMED_ERROR.value,
                                    message=f"Falha ao ler o arquivo: {exc}", source_file=item.source.source_id,
                                    recommended_action="Verificar formato/integridade e dependências (xlrd, odfpy).",
                                    stage="reading"))
            _mark_file(res, item.source.source_id, "ERRO_LEITURA")
            log.error("Falha de leitura", extra={"source": item.source.source_id, "error": str(exc)})
            continue
        for grid in grids:
            _process_sheet(grid, cfg, vocab, symbols, resolver, res)
    res.timings["adapters"] = time.perf_counter() - t1

    # 3b) conferência com o guia oficial de tabelas -------------------------
    ref_issues, res.reference_report, ref_checks = check_against_guide(
        res.sheets, cfg.optional_csv("reference/guia_tabelas_pense_2024.csv"))
    res.issues.extend(ref_issues)

    # 3c) pergunta de origem (dicionários do IBGE) -----------------------------
    questions_linked = apply_questions(res.estimates, build_question_map(cfg))

    # 4) normalização ---------------------------------------------------
    t2 = time.perf_counter()
    z = float(cfg.v("validation", "z_value_95"))
    cv_issues, cv_compared = join_cv(res.estimates, res.cv_records)
    res.issues.extend(cv_issues)
    for rec in res.estimates:
        derive_standard_error(rec, z)
        rec["data_stage"] = "normalized"

    # 5) validação ------------------------------------------------------
    validator = Validator(ValidationSettings.from_config(cfg.settings["validation"]), cfg.symbols)
    val_issues = validator.run(res.estimates)
    res.issues.extend(val_issues)
    res.rule_checks = dict(sorted(validator.checks.items()))
    res.rule_checks["VAL010"] = cv_compared
    res.rule_checks.update(ref_checks)
    res.rule_checks["QST_perguntas_ligadas"] = questions_linked
    assign_status(res.estimates, res.issues)
    for rec in res.estimates:
        rec["data_stage"] = "validated"
        rec.setdefault("analytical_duplicate_of", "")
    res.timings["validation"] = time.perf_counter() - t2

    # 6) harmonização ---------------------------------------------------
    res.comparability = evaluate(res.estimates, cfg.optional_csv("comparability_candidates.csv"),
                                 cfg.optional_csv("comparability_decisions.csv"))
    idx = status_index(res.comparability)
    for rec in res.estimates:
        rec["comparability_status"] = idx.get((rec["indicator_id"], rec["response_category"]),
                                              "SEM_CORRESPONDENTE_IDENTIFICADO")
    res.catalog = build_catalog(res.estimates, idx)

    # 7) série histórica ------------------------------------------------
    res.series, res.series_summary, res.series_status = build_series(
        res.estimates, res.comparability, sorted(cfg.editions),
        bool(cfg.v("historical", "allow_descriptive_mean")))
    # 8) microdados (opcional): série harmonizada a partir de estimativas já calculadas -------
    res.micro = load_microdata_outputs(cfg, res.estimates)
    res.timings["total"] = time.perf_counter() - t0
    if write_outputs:
        _write(cfg, res)
    _log_summary(res)
    return res


def _process_sheet(grid: Any, cfg: Config, vocab: Vocab, symbols: frozenset[str], resolver: TerritoryResolver,
                   res: RunResult) -> None:
    title, rows = extract_title(grid)
    notes, _ = extract_footnotes(grid, (max(rows) + 1) if rows else 0)
    info = parse_title(title, notes)
    info.title_rows = rows
    ctx = SheetContext(grid, info, cfg, vocab, symbols, resolver)
    sel = select_adapter(ctx)
    sheet_row = {
        "source_file": grid.source.source_id, "sheet": grid.sheet, "sheet_index": grid.sheet_index,
        "rows": grid.nrows, "columns": grid.ncols, "nonempty_cells": grid.nonempty_count(),
        "merged_ranges": len(grid.merges), "merge_info": grid.merge_info, "table_id": info.table_id,
        "year": info.year, "year_method": info.year_method, "footer_year": info.footer_year,
        "sample": info.sample, "population": info.population, "territorial_scope": info.territorial_scope,
        "estimate_type": info.estimate_type, "is_cv_sheet": info.is_cv_sheet, "title": info.title,
        "adapter_family": sel.adapter.family_id if sel.adapter else "",
        "detection_score": round(sel.detection.score, 2) if sel.detection else 0,
        "detection_evidence": " | ".join(sel.detection.evidence) if sel.detection else "",
        "candidates": "; ".join(f"{f}={s}" for f, s in sel.candidates), "selection_reason": sel.reason,
        "records": 0, "issues": 0, "status": "",
    }
    if sel.adapter is None:
        sheet_row["status"] = "NAO_MAPEADA"
        res.unparsed.append({"source_file": grid.source.source_id, "source_sheet": grid.sheet, "kind": "sheet",
                             "cell": "", "detail": f"Nenhum adaptador: {sel.reason}"})
        res.issues.append(Issue(rule_id="ADP000", severity=Severity.REVIEW.value,
                                issue_class=IssueClass.NOT_VALIDATED.value,
                                message=f"Aba sem adaptador ({sel.reason})", source_file=grid.source.source_id,
                                source_sheet=grid.sheet, table_id=info.table_id,
                                recommended_action="Criar adaptador para a família ou ajustar a detecção.",
                                stage="adapter-selection"))
        res.sheets.append(sheet_row)
        return
    try:
        out = sel.adapter.extract(ctx)
    except Exception as exc:  # resiliência: uma aba com erro não derruba a execução
        log.exception("Falha no adaptador", extra={"source": grid.source.source_id, "sheet": grid.sheet})
        res.issues.append(Issue(rule_id="ADP900", severity=Severity.ERROR.value,
                                issue_class=IssueClass.CONFIRMED_ERROR.value,
                                message=f"Exceção no adaptador {sel.adapter.family_id}: {type(exc).__name__}: {exc}",
                                source_file=grid.source.source_id, source_sheet=grid.sheet, table_id=info.table_id,
                                recommended_action="Corrigir o adaptador; ver logs/pipeline.jsonl.",
                                stage="adapter"))
        sheet_row["status"] = "ERRO_ADAPTADOR"
        res.sheets.append(sheet_row)
        return
    if info.year and info.footer_year and info.year != info.footer_year:
        for r in out.records:
            r["extraction_flags"] = "|".join(filter(None, [r["extraction_flags"], "ANO_INCONSISTENTE"]))
    for r in out.records:
        r["data_stage"] = "extracted"
    (res.cv_records if sel.adapter.record_kind == "cv" else res.estimates).extend(out.records)
    res.issues.extend(out.issues)
    res.unparsed.extend(out.unparsed)
    sheet_row.update(records=len(out.records), issues=len(out.issues),
                     status="EXTRAIDA" if out.records else "SEM_REGISTROS")
    res.sheets.append(sheet_row)


def _mark_file(res: RunResult, source_id: str, status: str) -> None:
    for f in res.files:
        if f["source_id"] == source_id:
            f["status"] = status


def _write(cfg: Config, res: RunResult) -> None:
    staging, processed, curated = cfg.path("staging"), cfg.path("processed"), cfg.path("curated")
    fields = CANONICAL_FIELDS + INTERNAL_FIELDS
    write_csv(processed / "inventory_files.csv", res.files)
    write_csv(processed / "inventory_sheets.csv", res.sheets)
    extracted = [dict(r, data_stage="extracted") for r in res.estimates + res.cv_records]
    write_csv(staging / "observations_extracted.csv", extracted, fields)
    write_csv(processed / "observations_normalized.csv",
              [dict(r, data_stage="normalized") for r in res.estimates], fields)
    write_csv(processed / "observations_validated.csv", res.estimates, fields)
    issue_rows = sorted((i.to_dict() for i in res.issues),
                        key=lambda d: ({"ERROR": 0, "REVIEW": 1, "WARNING": 2, "INFO": 3}[d["severity"]],
                                       d["rule_id"], d["source_file"], d["source_sheet"], d["source_cell"]))
    write_csv(processed / "quality_issues.csv", issue_rows)
    if res.reference_report:
        write_csv(processed / "reference_check_guia_2024.csv", res.reference_report)
    write_csv(processed / "unparsed_report.csv", res.unparsed,
              ["source_file", "source_sheet", "kind", "cell", "detail"])
    approved = [dict(r, data_stage="approved") for r in res.estimates
                if r.get("approved_for_analysis") and not r.get("analytical_duplicate_of")]
    write_csv(curated / "pense_observations_approved.csv", approved, CANONICAL_FIELDS)
    write_json(curated / "pense_observations_approved.json",
               [{k: r.get(k) for k in SLIM_FIELDS} for r in approved], compact=True)
    write_csv(curated / "indicator_catalog.csv", res.catalog)
    write_csv(curated / "comparability_catalog.csv", res.comparability)
    series_fields = ["series_id", "concept_id", "comparability_status", "territory_code", "territory_name",
                     "territory_type", "age_group", "sex", "admin_dependency", "year", "edition_id", "indicator_id",
                     "response_category", "unit", "estimate", "ci_lower", "ci_upper", "coefficient_of_variation",
                     "previous_year", "abs_change", "abs_change_unit", "rel_change_pct", "observation_id",
                     "source_file", "source_cell", "comparability_note", "interpretation_note"]
    write_csv(curated / "historical_series.csv", res.series, series_fields)
    write_csv(curated / "historical_series_summary.csv", res.series_summary,
              ["series_id", "territory_code", "age_group", "sex", "admin_dependency", "n_points", "years",
               "first_year", "last_year", "editions_without_point", "comparability_status", "descriptive_mean",
               "descriptive_mean_note", "interpretation_note"])
    write_csv(curated / "historical_series_status.csv", res.series_status)
    summary = issues_summary(res.issues)
    bundle = build_bundle(res.estimates, res.catalog, res.comparability, res.series, res.series_status,
                          cfg.territories, summary, cfg.editions, __version__, cfg.symbols,
                          {r["indicator_id"]: r for r in cfg.optional_csv("indicator_labels.csv")})
    if res.micro:
        bundle["micro"] = res.micro["bundle"]
        stamp_hash(bundle)
        write_csv(curated / "microdata_comparability.csv", res.micro["comparability"])
        write_csv(curated / "microdata_series.csv", res.micro["series"])
        write_csv(cfg.config_dir / "microdata" / "comparability_decisions_MODELO.csv", res.micro["decision_template"])
        for msg in res.micro.get("invalid_decisions", []):
            log.warning("Decisão de comparabilidade ignorada", extra={"detail": msg})
    write_json(cfg.path("dashboard_data") / "pense_bundle.json", bundle, compact=True)
    manifest = {
        "pipeline_version": __version__,
        "executed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "python": sys.version.split()[0], "platform": platform.platform(),
        "libraries": _lib_versions(),
        "inputs": [{k: f[k] for k in ("source_id", "sha256", "size_bytes", "status", "duplicate_of")} for f in res.files],
        "counts": run_counts(res),
        "rule_checks": res.rule_checks,
        "dashboard_bundle_sha256": bundle["meta"]["content_sha256"],
        "timings_seconds": {k: round(v, 2) for k, v in res.timings.items()},
    }
    write_json(processed / "run_manifest.json", manifest)
    write_reports(cfg, res, manifest)


def issues_summary(issues: list[Issue]) -> list[dict[str, Any]]:
    c = Counter((i.rule_id, i.severity, i.issue_class) for i in issues)
    return [{"rule_id": r, "severity": s, "issue_class": k, "count": n}
            for (r, s, k), n in sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))]


def run_counts(res: RunResult) -> dict[str, Any]:
    st = Counter(r["validation_status"] for r in res.estimates)
    return {
        "files_inventoried": len(res.files),
        "files_unique": sum(1 for f in res.files if not f["duplicate_of"] and f["format"] != "zip"),
        "duplicates": sum(1 for f in res.files if f["duplicate_of"]),
        "sheets": len(res.sheets),
        "sheets_by_family": dict(Counter(s["adapter_family"] or "NAO_MAPEADA" for s in res.sheets)),
        "estimate_records": len(res.estimates),
        "cv_records": len(res.cv_records),
        "validation_status": dict(st),
        "approved_canonical": sum(1 for r in res.estimates if r.get("approved_for_analysis")
                                  and not r.get("analytical_duplicate_of")),
        "analytical_duplicates": sum(1 for r in res.estimates if r.get("analytical_duplicate_of")),
        "issues_by_severity": dict(Counter(i.severity for i in res.issues)),
        "indicators": len({r["indicator_id"] for r in res.estimates}),
        "measures": len(res.catalog),
        "comparability_pairs": len(res.comparability),
        "comparability_status": dict(Counter(p["final_status"] for p in res.comparability)),
        "series_points": len(res.series),
        "unparsed_items": len(res.unparsed),
        "microdata_estimates": len(res.micro.get("estimates", [])),
        "microdata_series_points": len(res.micro.get("series", [])),
        "microdata_comparability": dict(Counter(c["final_status"] for c in res.micro.get("comparability", []))),
    }


def _lib_versions() -> dict[str, str]:
    out = {}
    for mod in ("openpyxl", "xlrd", "odf"):
        try:
            m = __import__(mod)
            out[mod] = getattr(m, "__version__", "") or getattr(m, "version", "")
        except ImportError:
            out[mod] = "ausente"
    return {k: str(v) for k, v in out.items()}


def _log_summary(res: RunResult) -> None:
    c = run_counts(res)
    log.info(f"Arquivos: {c['files_inventoried']} inventariados ({c['duplicates']} duplicados); abas: {c['sheets']}")
    log.info(f"Observações de estimativa: {c['estimate_records']}; CV: {c['cv_records']}; "
             f"aprovadas (canônicas): {c['approved_canonical']}")
    log.info(f"Status: {c['validation_status']}")
    log.info(f"Alertas por severidade: {c['issues_by_severity']}")
    log.info(f"Pares de comparabilidade: {c['comparability_status']}; pontos de série: {c['series_points']}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Pipeline PeNSE — ingestão a dashboard")
    ap.add_argument("-v", "--verbose", action="store_true", help="log detalhado no console")
    args = ap.parse_args(argv)
    res = run(verbose=args.verbose)
    errors = sum(1 for i in res.issues if i.severity == "ERROR" and i.stage in ("reading", "adapter"))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
