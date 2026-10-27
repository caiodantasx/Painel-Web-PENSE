# Relatório de auditoria do código anterior (pense_pipeline_v2)

Data da auditoria: 26/10/2026. Objeto: `pense_pipeline_harmonizacao_historica.zip`
(gerado anteriormente com outra ferramenta) e os arquivos de dados do projeto.

## 1. O que existia

| Item | Situação encontrada |
|---|---|
| Código | um único `run_pipeline.py` (171 linhas), sem módulos, tipagem ou testes |
| Dashboard | não incluído no pacote |
| Configuração | `config/mapeamento_validado.csv` apenas com cabeçalho |
| Saídas | inventário de abas, dump de 71 mil células, alertas heurísticos; `base_analitica.csv` e `serie_historica.csv` **vazias** |
| Dependências | `requirements.txt` sem limites superiores; `xlrd` não estava instalado na execução registrada |

## 2. Problemas identificados

| # | Problema | Evidência | Impacto |
|---|---|---|---|
| 1 | Nenhum adaptador: nada chega à base canônica | `build_historical()` grava DataFrames vazios | o dashboard não teria dados reais |
| 2 | Arquivo XLS 2015 não lido | `anomalias.csv`: "Missing optional dependency 'xlrd'" | edição inteira perdida, sem falha visível no resumo |
| 3 | Bug no catálogo de comparabilidade | `column_counts` usa `grp.columns` (nomes das colunas do DataFrame) em vez de `grp["columns"]` | catálogo grava "file \| file_name \| …" no lugar das contagens |
| 4 | Falso alarme de percentual > 100 | `100.00000000000016` (17.2.2) reportado como fora de 0–100 | ruído na revisão |
| 5 | Ano por "primeiro número 20xx" no texto | `detect_year` | risco de ano errado em títulos que citam outras datas |
| 6 | Cabeçalho por "5 linhas acima" | `header_context` | não distingue estimativa, IC e CV; ignora células mescladas |
| 7 | Território só nas 5 primeiras colunas, sem escopo | `TERRITORIES` | "Total" das capitais, "Distrito Federal" (capital em 2009) e "São Luis" não resolvidos |
| 8 | ZIP extraído para disco a cada execução | `expand_archives` | pastas duplicadas (`…_1` e `…_1_`), risco de *zip slip* tratado só parcialmente |
| 9 | Duplicatas por hash só dentro da mesma execução | `get_files` | correto, mas sem registro das duplicatas no inventário |
| 10 | Sem testes, sem logs estruturados, sem manifesto de versões | — | reprodutibilidade não demonstrável |

## 3. Riscos estatísticos encontrados nos dados

* **Populações diferentes entre edições:** 2009 e 2015 = escolares do 9º ano; 2024 =
  escolares de 13 a 17 anos. Combinar em série seria erro metodológico.
* **Denominadores condicionais** (17.2 "por número de vezes", 9.13 "dentre aqueles que…",
  9.3 "dentre aqueles que andaram de moto") exigem denominador explícito por observação.
* **Múltipla resposta** (9.18, 9.20, 9.22): categorias não somam 100%.
* **Não-resposta não apresentada** (9.14, 9.15, 9.23, 17.2): categorias somam menos de 100%.
* **Cabeçalho assimétrico** em 2009 tab 8.1 (ver `03_adaptadores_por_familia.md`).
* **Símbolo "-"** em 2015 não pode virar zero sem decisão documentada.

## 4. Decisão: reconstrução

Diante dos itens 1, 3, 6 e 7, a pipeline foi **reconstruída** como pacote modular
(`src/pense/`), aproveitando as ideias corretas do código anterior: hash SHA-256,
descarte de duplicatas, proteção contra *zip slip*, preservação da origem e status
`PENDENTE` em vez de inferência. Detalhes em `04_decisoes_metodologicas.md`.

## 5. Resultado da nova pipeline (execução de 26/10/2026)

| Medida | Valor |
|---|---|
| Arquivos inventariados / únicos / duplicados | 41 / 36 / 2 |
| Abas lidas / com família reconhecida | 173 / 173 |
| Observações de estimativa / linhas de CV | 14.707 / 12.463 |
| Aprovadas para análise (canônicas) | 13.661 |
| Em revisão / indisponíveis (símbolo) | 56 / 120 |
| Estimativas conferidas entre aba principal e aba de CV | 12.459, 0 divergências |
| Coerência CV × IC (erro-padrão derivado) | 12.128 conferidas, diferença máx. 0,07% |
| Mesmo recorte em tabelas diferentes (ex.: Brasil em 17.1.1 e 17.1.2) | 870 pares, 0 divergências |
| Pares de comparabilidade avaliados | 16, todos `NOT_COMPARABLE` |
| Testes automatizados | 105 aprovados (100 da pipeline + 5 do painel) |
| Tempo total | ≈ 6 s |
