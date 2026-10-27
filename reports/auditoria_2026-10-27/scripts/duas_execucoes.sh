#!/usr/bin/env bash
# Executa run_all duas vezes no projeto limpo e guarda os SHA-256 das saídas determinísticas.
set -u
P=/tmp/claude-0/limpo; PY=/tmp/claude-0/venv_limpo/bin/python; OUT=/home/claude/auditoria/repro
mkdir -p "$OUT"
hashes() { (cd "$P" && find data/staging data/processed data/curated dashboard/data docs reports -type f -print0 | sort -z | xargs -0 sha256sum) > "$1"; }
cd "$P"
for i in 1 2; do
  start=$(date +%s); "$PY" scripts/run_all.py > "$OUT/run_all_$i.log" 2>&1; rc=$?; end=$(date +%s)
  echo "execução $i: código $rc, $((end-start)) s" >> "$OUT/resumo.txt"
  hashes "$OUT/hashes_$i.txt"
done
"$PY" -m pytest -q -p no:cacheprovider -rs > "$OUT/pytest_venv_limpo.log" 2>&1; echo "pytest venv limpo: código $?" >> "$OUT/resumo.txt"
