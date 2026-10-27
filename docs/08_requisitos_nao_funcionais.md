# Matriz de requisitos não funcionais

Status: **Atendido** (implementado e verificado por teste/execução), **Parcial**
(implementado com limitação conhecida) ou **Pendente**.

| ID | Requisito | Critério de aceitação | Evidência / teste | Status |
|---|---|---|---|---|
| RNF01 | Reprodutibilidade | Mesmas entradas → saídas idênticas; versões e hashes registrados | `test_run_is_idempotent`; `run_manifest.json` (hash de entradas, versões, hash do pacote do painel); dependências com faixa de versão em `pyproject.toml` | Atendido |
| RNF02 | Rastreabilidade e auditabilidade | Todo valor aprovado remete a arquivo, aba e célula | `test_every_approved_value_traces_back_to_its_source_cell` (reabre os arquivos originais); `test_2024_estimate_ci_and_traceability`; `quality_issues.csv` com célula | Atendido |
| RNF03 | Acessibilidade | Teclado, rótulos, foco visível, contraste, alternativa textual a gráficos | `test_keyboard_navigation_and_labels`; paleta validada (CVD e contraste, claro/escuro); tabela para cada gráfico; status com forma + texto; `forced-colors` | Parcial: sem auditoria com leitor de tela real nem teste com usuários |
| RNF04 | Responsividade ≥ 360 px | Sem rolagem horizontal; layout em uma coluna | `test_mobile_360_has_no_horizontal_scroll` (visão geral, territórios, qualidade) | Atendido |
| RNF05 | Robustez a arquivos malformados | Falha de um arquivo não interrompe os demais | `test_failure_in_one_file_does_not_stop_others`; `test_corrupted_zip_and_unsupported_files_are_reported_not_fatal`; `ADP900` captura exceção por aba | Atendido |
| RNF06 | Segurança no tratamento de arquivos | ZIP sem escrita em disco, limites de tamanho/membros, caminhos suspeitos registrados | `test_zip_slip_names_never_touch_disk`; `test_nested_zip_respects_depth_limit`; `settings.toml [ingestion]` | Atendido |
| RNF07 | Desempenho | Base completa em segundos | execução completa ≈ 6 s (36 arquivos, 173 abas); painel ≈ 1,4 MB de dados | Atendido |
| RNF08 | Manutenibilidade | Módulos por responsabilidade, configuração externa, nova família sem reescrever o motor | estrutura `src/pense/*`; `docs/05_guia_novas_tabelas.md`; famílias com ~40 linhas cada | Atendido |
| RNF09 | Mensagens de erro úteis | Todo alerta com regra, contexto, célula e ação recomendada | `Issue` (`models.py`); relatório de qualidade | Atendido |
| RNF10 | Separação desenvolvimento × produção | Dados de teste nunca no painel; build estático separado | fixtures sintéticas só em `tests/`; `test_bundle_values_come_from_pipeline_records`; `scripts/build_dashboard.py` → `dist/` | Atendido |
| RNF11 | Integridade dos dados | Nada inventado, corrigido ou removido silenciosamente | `test_validation_never_removes_records`; `test_symbols_are_not_converted_to_zero`; `test_percent_out_of_range_is_error_but_float_artifact_is_info` | Atendido |
| RNF12 | Comparabilidade metodológica | Séries só com pares aprovados e justificados | `test_incompatible_tables_are_never_combined`; `test_identical_attributes_never_become_comparable_automatically`; `test_human_decision_requires_justification` | Atendido |
| RNF13 | Sem dependências pagas ou serviços externos | Execução offline | pipeline: openpyxl, xlrd, odfpy; painel: sem bibliotecas (fontes Google opcionais, com fallback) | Atendido |
| RNF14 | Logging estruturado | Logs com severidade e contexto | `logs/pipeline.jsonl` | Atendido |
