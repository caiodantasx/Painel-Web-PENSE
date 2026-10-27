# Pipeline e painel PeNSE — Segurança na escola

Sistema reprodutível que transforma tabelas oficiais da **Pesquisa Nacional de Saúde do
Escolar (PeNSE/IBGE)** — publicadas em XLS, XLSX e ZIP, com estruturas diferentes entre
edições — em uma base analítica padronizada, rastreável e validada, consumida por um
painel web inspirado no Power BI.

* **Rastreabilidade:** cada valor guarda arquivo, aba, linha, coluna e célula de origem.
* **Integridade:** nenhum número é inventado, corrigido ou removido; alertas explicam o
  que precisa de revisão.
* **Comparabilidade:** séries históricas só com indicadores de mesma definição; com os
  microdados (2015 Amostras 1 e 2, 2019, 2024) o mesmo indicador é recalculado em cada
  edição, com a mesma convenção de não resposta, e validado contra as tabelas publicadas.
  A pipeline só **propõe** comparabilidade; o selo "Diferença significativa a 5%" exige decisão registrada
  pelo pesquisador (`docs/06`, D21–D23 em `docs/04`).

## Execução rápida

Requer Python ≥ 3.11.

```bash
# Windows (PowerShell)
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Linux/macOS
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python scripts/extract_microdata.py <pasta_com_os_zips_do_ibge>   # opcional: microdados (confere SHA-256)
python scripts/run_all.py             # pipeline + microdados (se presentes) + docs + painel
python -m pytest                      # testes (os do painel exigem playwright; os de recálculo, microdados)
python -m http.server -d dashboard 8000   # abra http://localhost:8000
```

O painel precisa ser servido por HTTP (o navegador bloqueia `fetch` em `file://`).
Para publicar (GitHub Pages, Netlify), gere a pasta estática:
`python scripts/build_dashboard.py` → `dist/dashboard/`.

## Entradas

Coloque arquivos em `data/raw/` (subpastas permitidas): `.xlsx`, `.xlsm`, `.xls`,
`.ods`, `.csv` ou `.zip` contendo esses formatos. ZIPs são lidos em memória (sem
extração para disco) e arquivos idênticos (mesmo SHA-256) são processados uma vez.

Arquivos atualmente na base: PeNSE 2009 (`tab08avs.zip`), PeNSE 2015 Amostra 1
(`Amostra_1_Tema_06_Seguranca_da_Escola.xls`), PeNSE 2015 Amostra 2 (Tema 11,
`Amostra_2_Tema_11_Seguranca_2015.xls`), PeNSE 2019 (Temas 9 e 17), PeNSE 2024 (Temas 9 e
17, em ZIP) e a série oficial do 9º ano 2009–2019 (Tema 10). Cerca de 33 mil estimativas
extraídas.

**Microdados (opcional, não versionados — cerca de 390 MB):** baixe os ZIPs do IBGE e rode
`python scripts/extract_microdata.py <pasta>`. O manifesto `config/microdata/source_files.csv`
lista, por edição (2009, 2012, 2015 A1 e A2, 2019, 2024), o arquivo dentro do ZIP, o destino em
`data/microdata/<EDIÇÃO>/`, o tamanho e o SHA-256. Particularidade de 2009: o original se chama
`Base_Pense Completa_2009.txt` (com espaço) e é gravado como `Base_Pense_Completa_2009.txt`.
Sem microdados a pipeline roda normalmente com as tabelas publicadas. Ver `docs/12_microdados.md`.

**Documentos de referência:** `data/reference/` (guia de tabelas 2024, questionário do
aluno 2015) → `config/reference/` por `scripts/build_reference.py`
(ver `docs/11_documentos_de_referencia.md`).

## Saídas e camadas de dados

| Camada | Arquivo | Conteúdo |
|---|---|---|
| bruto | `data/raw/` | arquivos originais, nunca alterados |
| inventário | `data/processed/inventory_files.csv`, `inventory_sheets.csv` | hash, formato, abas, família detectada e evidência |
| extraído | `data/staging/observations_extracted.csv` | estimativas e linhas de CV como lidas |
| normalizado | `data/processed/observations_normalized.csv` | CV anexado, erro-padrão derivado (rotulado) |
| validado | `data/processed/observations_validated.csv` | status de validação e regras acionadas |
| alertas | `data/processed/quality_issues.csv` | regra, severidade, classe, célula, ação recomendada |
| não interpretado | `data/processed/unparsed_report.csv` | abas, colunas ou linhas que a pipeline não entendeu |
| aprovado | `data/curated/pense_observations_approved.csv` / `.json` | só observações válidas, sem duplicidade entre tabelas |
| catálogos | `data/curated/indicator_catalog.csv`, `comparability_catalog.csv` | indicadores e decisões de comparabilidade |
| série | `data/curated/historical_series*.csv` | pontos, resumo e status de cada par candidato |
| microdados | `data/curated/microdata_estimates.csv` | indicadores recalculados (origem `MICRODADOS_CALCULADO`) |
| validação | `data/curated/microdata_validation*.csv` | cálculo × tabela publicada, recorte a recorte |
| série harmonizada | `data/curated/microdata_series.csv`, `microdata_comparability.csv` | pontos (só edições com evidência), diferença entre anos com IC 95% e estado (`change_status`), proposta × decisão |
| não resposta | `data/curated/microdata_nonresponse_effect.csv` | efeito medido da harmonização por indicador e edição |
| evidências | `data/curated/methodological_evidence_matrix.csv`, `docs/13_matriz_evidencias.md` | pergunta, informante, população, regras, validação, comparabilidade e limitações |
| painel | `dashboard/data/pense_bundle.json` | pacote colunar consumido pelo JavaScript |
| relatórios | `reports/*.md`, `data/processed/run_manifest.json` | qualidade, cobertura, comparabilidade, versões e hashes |

Formato: CSV (UTF-8 com BOM, abre no Excel) e JSON. Com cerca de 33 mil estimativas
publicadas, Parquet não traria ganho e exigiria `pyarrow`.

## Estrutura

```text
config/            regras e mapeamentos externos (territórios, vocabulário, símbolos,
                   edições, rótulos, pares e decisões de comparabilidade)
src/pense/
  ingestion/       descoberta de arquivos, ZIP seguro, leitores por formato
  parsing/         título, cabeçalho multinível (células mescladas), stub
  adapters/        famílias de tabelas e seleção por evidência
  standardization/ esquema canônico, territórios, junção de CV
  validation/      regras determinísticas e valores incomuns
  harmonization/   catálogo de indicadores e comparabilidade
  historical/      séries só para pares aprovados
  exports/         CSV/JSON e pacote do painel
  reporting/       relatórios Markdown
  pipeline.py      orquestração e CLI
dashboard/         painel (HTML/CSS/JS sem dependências de build)
scripts/           run_pipeline, build_dashboard, build_uf_geometry, generate_docs
tests/             pytest (unitários, regressão com tabelas reais, integração)
docs/              documentação do TCC
```

## Documentação

| Documento | Assunto |
|---|---|
| `docs/01_auditoria.md` | diagnóstico do código anterior e plano executado |
| `docs/02_arquitetura_e_manual_pipeline.md` | arquitetura, etapas, execução e logs |
| `docs/03_adaptadores_por_familia.md` | onde está cada informação em cada família de tabela |
| `docs/04_decisoes_metodologicas.md` | registro de decisões (ADR) |
| `docs/05_guia_novas_tabelas.md` | como adicionar tabelas, temas e edições |
| `docs/06_guia_serie_historica.md` | como interpretar e aprovar séries |
| `docs/07_manual_dashboard.md` | uso do painel |
| `docs/08_requisitos_nao_funcionais.md` | matriz de requisitos com teste e status real |
| `docs/09_relatorio_testes.md` | resultado da última execução dos testes |
| `docs/10_pendencias.md` | o que exige revisão humana ou ainda não foi implementado |
| `docs/12_microdados.md` | microdados: desenho, validação, série, efeito da não resposta (gerado) |
| `docs/13_matriz_evidencias.md` | matriz de evidências metodológicas por indicador e edição (gerado) |
| `docs/dicionario_de_dados.md` | dicionário gerado do esquema canônico |
