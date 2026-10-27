# Dicionário de dados — base canônica

Gerado automaticamente de `src/pense/standardization/schema.py` por `scripts/generate_docs.py`.
Uma linha da base = uma estimativa publicada (formato longo).

| Campo | Tipo | Descrição | Origem |
|---|---|---|---|
| `observation_id` | str | Identificador determinístico da observação (hash da origem). | pipeline |
| `data_stage` | str | Camada do dado: extracted, normalized, validated, approved. | pipeline |
| `source_file` | str | Arquivo de origem (ZIP!membro quando aplicável), relativo a data/raw. | origem |
| `source_container` | str | ZIP que continha o arquivo (vazio se arquivo solto). | origem |
| `source_hash` | str | SHA-256 do arquivo de origem. | origem |
| `source_sheet` | str | Nome da aba de origem. | origem |
| `source_row` | int | Linha da estimativa na planilha (numeração do Excel). | origem |
| `source_column` | str | Coluna da estimativa (letra do Excel). | origem |
| `source_cell` | str | Célula da estimativa (ex.: B13). | origem |
| `ci_lower_cell` | str | Célula do limite inferior do IC. | origem |
| `ci_upper_cell` | str | Célula do limite superior do IC. | origem |
| `cv_source` | str | Aba!célula de onde veio o coeficiente de variação. | origem |
| `adapter_family` | str | Família estrutural reconhecida pelo adaptador. | pipeline |
| `edition_id` | str | Edição da pesquisa (ex.: PENSE_2024). | título/rodapé |
| `edition_year` | int | Ano de referência do valor (da coluna/seção em tabelas multianuais). | título/rodapé/cabeçalho |
| `year_source` | str | De onde veio o ano: sufixo do título, rodapé ou cabeçalho/seção da tabela. | pipeline |
| `edition_sample` | str | Amostra (quando a edição tem mais de uma). | rodapé |
| `theme_id` | str | Tema/capítulo da publicação. | código da tabela |
| `table_id` | str | Código da tabela publicado (ex.: 17.1.2). | título |
| `table_family_id` | str | Código da tabela sem o recorte territorial (ex.: 17.1). | código da tabela |
| `territorial_cut` | str | Recorte territorial da aba (region, uf, capital). | título |
| `indicator_id` | str | Indicador específico da edição: EDIÇÃO__família. | pipeline |
| `indicator_name` | str | Enunciado do indicador conforme cabeçalho. | cabeçalho |
| `indicator_definition` | str | Enunciado completo extraído do título da tabela. | título |
| `question_text` | str | Texto da pergunta de origem, do dicionário de microdados do IBGE (PENDENTE se não ligado). | dicionário IBGE |
| `question_variable` | str | Variável dos microdados ligada à tabela (ano do dicionário). | dicionário IBGE |
| `question_source` | str | Como a tabela foi ligada à pergunta: reprodução numérica com microdados ou mapeamento manual. | pipeline |
| `reference_period` | str | Período de referência da pergunta (ex.: 30 dias anteriores à pesquisa). | título |
| `reference_period_code` | str | Código canônico do período (30_DIAS, 12_MESES, VIDA). | título |
| `population` | str | População de referência (universo). | título |
| `population_code` | str | Código normalizado da população. | título |
| `informant` | str | Quem informou (escolar ou escola/diretor). | título |
| `informant_method` | str | Como o informante foi determinado. | pipeline |
| `denominator` | str | Denominador da estimativa. | título/notas |
| `denominator_status` | str | EXTRAIDO_DO_TITULO, REGRA_DERIVADA_REVISAR ou PENDENTE. | pipeline |
| `territory_type` | str | country, region, uf, capital ou aggregate. | stub + dicionário |
| `territory_code` | str | Código do território (UF IBGE, município IBGE, BR, N, ...). | dicionário |
| `territory_name` | str | Nome canônico do território. | dicionário |
| `territory_label_original` | str | Rótulo do território como publicado. | origem |
| `uf_sigla` | str | Sigla da UF (UFs e capitais). | dicionário |
| `region_code` | str | Grande Região do território. | dicionário |
| `age_group` | str | Grupo de idade (Total quando não desagregado). | stub |
| `sex` | str | Sexo (Homem/Mulher; Total quando não desagregado). | cabeçalho/stub |
| `admin_dependency` | str | Dependência administrativa da escola (Pública/Privada/Total). | cabeçalho/stub |
| `row_group_label` | str | Rótulo de seção da linha, como publicado. | origem |
| `dimension_labels_original` | str | Rótulos originais das dimensões de coluna. | origem |
| `response_category` | str | Categoria de resposta/tipo (vazio = indicador geral). | cabeçalho |
| `category_code` | str | Código normalizado da categoria. | pipeline |
| `category_group` | str | Grupo da categoria (ex.: Distribuição percentual por número de vezes). | cabeçalho |
| `unit` | str | % ou escolares (contagem estimada). | cabeçalho |
| `estimate_type` | str | percentual, distribuicao_percentual ou total_estimado. | cabeçalho/título |
| `estimate` | float | Estimativa publicada (precisão original, sem arredondamento). | origem |
| `estimate_raw` | str | Conteúdo bruto da célula da estimativa. | origem |
| `estimate_symbol` | str | Símbolo publicado no lugar do número (-, .., x). | origem |
| `ci_lower` | float | Limite inferior do IC publicado. | origem |
| `ci_upper` | float | Limite superior do IC publicado. | origem |
| `confidence_level` | int | Nível de confiança do IC (95). | cabeçalho/título |
| `coefficient_of_variation` | float | CV publicado (%), vindo da aba (CV) correspondente. | origem |
| `standard_error` | float | Erro-padrão DERIVADO do IC simétrico (não publicado). | derivado |
| `standard_error_method` | str | Método da derivação do erro-padrão, quando houver. | pipeline |
| `multi_response` | bool | A pergunta admitia mais de uma resposta (somas não fecham 100%). | notas |
| `nonresponse_excluded` | bool | Nota informa exclusão de quem não respondeu. | notas |
| `methodological_note` | str | Notas de rodapé da tabela. | rodapé |
| `header_path` | str | Caminho completo do cabeçalho da coluna da estimativa (auditoria). | origem |
| `analytical_duplicate_of` | str | Se o mesmo recorte foi publicado em outra tabela, id da observação canônica. | validação |
| `extraction_flags` | str | Alertas estruturais do adaptador herdados pela observação. | adaptador |
| `validation_status` | str | VALID, VALID_WITH_WARNINGS, REVIEW_REQUIRED, ERROR, NOT_AVAILABLE. | validação |
| `issue_rules` | str | Regras de qualidade acionadas na observação. | validação |
| `approved_for_analysis` | bool | True se VALID ou VALID_WITH_WARNINGS e com estimativa numérica. | validação |
| `comparability_status` | str | Status de comparabilidade do indicador com outras edições. | harmonização |

Valores especiais: campos não identificáveis com segurança recebem `PENDENTE`; símbolos publicados ficam em `estimate_symbol` com `estimate` vazio.
