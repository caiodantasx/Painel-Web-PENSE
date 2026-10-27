# Adaptadores por família de tabela — onde está cada informação

Este documento responde, para cada família estrutural encontrada nos arquivos reais,
**onde estão** o indicador e a pergunta, o ano e a população, o território e a
desagregação, a estimativa, os limites do IC95% e as diferenças de definição entre
edições. Os números citados vêm da execução registrada em
`data/processed/run_manifest.json`.

## Como o reconhecimento funciona (comum a todas as famílias)

A família **não** é escolhida pelo nome do arquivo: cada adaptador pontua evidências
estruturais (código da tabela, ano no título e no rodapé, população, menção a IC ou a
CV, nome da aba) e a pipeline escolhe a maior pontuação ≥ 0,7, com margem mínima de
0,1 para o segundo colocado. A evidência fica gravada em
`data/processed/inventory_sheets.csv` (`detection_evidence`, `candidates`).

A leitura é comum às famílias e não presume posições de coluna:

1. **Título** (`parsing/title.py`): linha(s) que começam com "Tabela N.N…", juntadas
   até o sufixo "- AAAA" (2009 quebra o título em até 4 linhas).
2. **Cabeçalho** (`parsing/header.py`): para cada coluna, o caminho de rótulos de cima
   para baixo é montado a partir das **células mescladas reais** (XLSX via openpyxl,
   XLS via xlrd `formatting_info`, ODS via `number-columns-spanned`). O último rótulo
   define o papel da coluna (estimativa / limite inferior / limite superior / CV); os
   demais viram enunciado, dimensão (sexo, dependência) ou categoria de resposta,
   conforme `config/vocabulary.toml`.
3. **Stub** (`parsing/stub.py`): linhas sem valores são seções ("Total",
   "13 a 15 anos", "Homem", "Pública"); linhas com valores são territórios, resolvidos
   por `config/territories.csv` de acordo com o escopo lido do título.
4. **Rodapé**: "Fonte" (ano/amostra) e "Nota" (exclusões, não-resposta, múltipla resposta).

O que não for reconhecido gera alerta (`HDR001` coluna, `STB001` seção, `VAL012`
território, `ADP000` aba sem família) e entra em `data/processed/unparsed_report.csv`.
Na execução atual: **0 itens não interpretados**, **173 de 173 abas** com família.

---

## Família `PENSE_2024_IC` — PeNSE 2024, abas de estimativa (78 abas, 12.463 observações)

Arquivos: `Tabelas 9.1.xlsx` … `Tabelas 9.23.xlsx` (Tema 9 — Segurança) e
`Tabelas 17.1.xlsx` … `17.3.xlsx` (Tema 17 — Segurança da escola). Cada arquivo tem
três abas de estimativa: `x.y.1` (grupos de idade × Brasil e Grandes Regiões),
`x.y.2` (Brasil, Grandes Regiões e UFs) e `x.y.3` (municípios das capitais).

| Informação | Onde está | Exemplo verificado |
|---|---|---|
| Indicador | Título (A1, mesclado A1:…3) e enunciado do cabeçalho (linha 4, terminado em "(%)") | 17.1.1 → "Percentual de escolares de 13 a 17 anos em escolas cujo diretor(a)… presenciou ou ouviu falar… situações de violência na localidade…" |
| Pergunta de origem | **Não está nas tabelas.** Registrada como `PENDENTE` | Exige o questionário da PeNSE 2024 |
| Ano | Sufixo do título ("- 2024") **e** rodapé ("Pesquisa Nacional de Saúde do Escolar 2024"); divergência gera `VAL013` | 0 divergências |
| População | Título: "escolares de 13 a 17 anos" → `ESCOLARES_13_17_ANOS` | todas as 78 abas |
| Denominador | Título ("dentre aqueles que…", ex. 9.3, 9.13) e nota "Exclusive os escolares que…" (9.1, 9.2, 9.3) | 9.3 → "que andaram de motocicleta ou moto nos 30 dias…" |
| Informante | Título: "em escolas cujo diretor(a)…" → escola; caso contrário, escolar (marcado como inferido) | Tema 17 = escola; Tema 9 = escolar |
| Território | Coluna A do stub; escopo pelo final do título ("segundo … Grandes Regiões", "… Unidades da Federação", "… Municípios das Capitais") | Em `x.y.3`, a linha "Total" = conjunto das capitais (`CAPITAIS`) |
| Desagregação | **Linhas**: seções "13 a 17 anos"/"Total", "13 a 15 anos", "16 e 17 anos", "Homem", "Mulher", "Pública", "Privada". **Colunas**: "Sexo › Homem/Mulher", "Dependência Administrativa › Pública/Privada" | 9.x: idade nas linhas × sexo/dependência nas colunas (cruzamento publicado). 17.x: idade e dependência como seções separadas |
| Categoria de resposta | Rótulos de coluna que não são dimensão: tipos de violência (17.1, 17.3), banco (9.2), tipo de lesão (9.14), causa (9.15), agressor (9.18, 9.20, 9.22), idade da ocorrência (9.23), "Distribuição percentual por número de vezes › 1 vez / 2 vezes ou mais" (17.2) | 17.2: coluna "Total" = indicador principal; "1 vez"/"2 vezes ou mais" = distribuição condicional |
| Estimativa | Coluna cujo último rótulo é "Percentual"/"Percen-tual" | 17.1.1 B13 = 28,377891926889575 (Brasil, assaltos) |
| IC95% inferior/superior | Colunas "Intervalo de confiança de 95% › Limite inferior / Limite superior" do mesmo bloco | C13 = 24,66…, D13 = 32,09… |
| Notas | Rodapé "Nota:" — exclusões, não-resposta (9.14, 9.15, 9.23, 17.2), múltipla resposta (9.18, 9.20, 9.22) | gravadas em `methodological_note`, `nonresponse_excluded`, `multi_response` |

Particularidades tratadas:
* valores como `100.00000000000016` são artefatos de ponto flutuante — preservados e
  registrados como `VAL002F` (informativo);
* ICs truncados em 0 ou 100 (`VAL006`) e ICs de amplitude zero (`VAL005`, 44 casos,
  típicos de recortes com pouquíssimas escolas);
* o símbolo `..` aparece em 4 células de estimativa e é mantido como indisponível.

## Família `PENSE_2024_CV` — PeNSE 2024, abas "(CV)" (78 abas, 12.463 linhas)

Mesma gramática da família anterior, com blocos "Percentual | CV" no lugar do IC. As
linhas **não** viram observações próprias: o CV é **anexado** à observação de
estimativa com a mesma chave (tabela, território, recortes, categoria).

| Informação | Onde está |
|---|---|
| CV | Coluna cujo último rótulo é "CV", pareada à coluna "Percentual" do mesmo bloco |
| Estimativa repetida | Coluna "Percentual" — usada para **conferir** a aba principal (`VAL010`) |

Resultados: 12.459 estimativas conferidas entre aba principal e aba de CV, **0
divergências**. O erro-padrão derivado do IC simétrico, `(LS − LI) / (2 × 1,96)`,
coincide com o CV publicado em 12.128 observações (diferença relativa máxima de 0,07%),
o que confirma que estimativa, IC e CV foram associados às colunas corretas.

## Família `PENSE_2009_CAPITAIS` — PeNSE 2009, XLS legado (13 abas, 1.512 observações)

Arquivos: `tab801.xls` … `tab809.xls` dentro de `tab08avs.zip`. `tab802.xls` tem cinco
abas de continuação (`continua`, `continuacaoA/B/C`, `conclusao`), cada uma com um
recorte diferente indicado **no cabeçalho** (Total, Sexo › Feminino, Sexo ›
Masculino, Dependência › Privada, Dependência › Pública).

| Informação | Onde está | Observação |
|---|---|---|
| Indicador | Título em 4 linhas (A1:A4, cada linha mesclada) | juntado até "- 2009" |
| Ano | Sufixo do título e rodapé "…Escolar 2009." | — |
| População | "escolares frequentando o 9º ano do ensino fundamental"; 8.8 restringe a "menores de 18 anos" | `ESCOLARES_9ANO_EF` / `…_MENORES_18` |
| Período | "nos últimos 30 dias" → `30_DIAS` | equivalente a "30 dias anteriores à pesquisa" (2024) |
| Território | Apenas municípios das capitais; a linha "Total" é o conjunto das capitais; a capital do DF aparece como "Distrito Federal" e "São Luís" como "São Luis" | resolvidos por alias no escopo `capital` |
| Desagregação | Colunas "Sexo › Feminino/Masculino" e "Dependência administrativa da escola › Privada/Pública" | rótulos originais preservados em `dimension_labels_original` (Feminino → Mulher) |
| Estimativa | Coluna cujo último rótulo é **"Total"** (não "Percentual") ao lado do IC | o vocabulário trata "Total" folha como estimativa |
| IC95% | "Intervalo de confiança de 95% › Limite infe-rior / supe-rior" (hifenização com quebra de linha) | normalizado pela forma compacta do rótulo |
| CV | Não publicado | — |

Pendências desta família:
* **Tabela 8.1 — cabeçalho assimétrico (`HDR006`, 56 observações em revisão).** Há colunas
  por local ("Trajeto casa-escola", "Escola") e colunas por dependência (Privada,
  Pública) **sem** coluna de total geral. Pelo cabeçalho não dá para afirmar se as
  colunas de dependência se referem a "trajeto **ou** escola". Elas foram extraídas como
  indicador geral, marcadas `REVIEW_REQUIRED` e ficam fora da análise até consulta à
  publicação.
* Tabela 8.5, Macapá, Privada: limite inferior publicado = −0,247 (IC normal não
  truncado em 2009). Valor preservado (`VAL002N`).

## Família `PENSE_2015_A1` — PeNSE 2015 Amostra 1, XLS (4 abas, 732 observações)

Arquivo `Amostra_1_Tema_06_Seguranca_da_Escola.xls`: abas `1.1.6.1` e `1.1.6.2`
(Brasil, Grandes Regiões e UFs) e `1.2.6.1`, `1.2.6.2` (capitais).

| Informação | Onde está | Observação |
|---|---|---|
| Indicador | Título e **dois enunciados** no cabeçalho: "Estimativa total de escolares…" (contagem) e "Percentual de escolares… (%)" | a mesma aba gera duas medidas: `unit = escolares` e `unit = %` |
| Código | `1.<recorte>.<tema>.<tabela>`: 1.1.6.1 (UF) e 1.2.6.1 (capitais) são o mesmo indicador | família `1.6.1` / `1.6.2` |
| Ano/amostra | Rodapé "…Escolar, Amostra 1, 2015." | `edition_sample = Amostra 1` |
| População | "escolares frequentando o 9º ano do ensino fundamental" | informante: escola ("escolas que informaram…") |
| Território | Coluna A; "Total" nas abas de capitais = conjunto das capitais; "Brasília" | — |
| Desagregação | "Dependência Administrativa › Pública/Privada" | sem idade e sem sexo |
| Estimativa / IC | Folha "Total" + "Limite inferior/superior" | ICs truncados em 0 |
| Símbolo | `-` em 116 células (ex.: Privada em Rondônia, Roraima; DF inteiro em 1.1.6.2) | mantido como símbolo, **não** convertido em zero (`VAL001`) |

Validação específica: para contagens, Total ≈ Pública + Privada (`VAL019`, 74
conferências, 0 alertas). O mapa coroplético é desativado para contagens no painel.

---

## PENSE_MULTIANO — tabelas com vários anos na mesma aba (salvaguarda)

Nenhum arquivo fornecido tem esse formato: os anos presentes são 2009 (tab801–tab809),
2015 (Amostra 1, Tema 6) e 2024 (Temas 9 e 17), cada um em tabelas próprias. A família
existe para que uma tabela futura do tipo "… – 2009-2015" não seja atribuída a um só ano.

| Informação | Onde está | Tratamento |
|---|---|---|
| Intervalo de anos | sufixo do título com lista ("- 2009-2015", "- 2009, 2012 e 2015") | `multi_year = True`; o título **não** define o ano de nenhum valor |
| Ano de cada valor | rótulo de coluna ("2009", inclusive número `2009.0` do .xls) ou seção de linha | dimensão `year`, nunca categoria; `edition_year` e `edition_id = PENSE_<ano>` por valor; `year_source = cabeçalho/seção da tabela`; alerta informativo `VAL024` |
| Valor sem ano identificável | — | `ANO_INDEFINIDO` → `VAL025` (revisão), `edition_year` vazio, fora da análise |

Testes: `tests/test_multiyear.py`.

---

## Diferenças de definição entre edições (resumo)

| Conceito | 2009 | 2015 (A1) | 2024 | Conclusão automática |
|---|---|---|---|---|
| Universo | 9º ano do EF (capitais) | 9º ano do EF | 13 a 17 anos | **populações diferentes** |
| Faltar por insegurança | 8.1: trajeto **ou** escola, por local | — | 9.7 (trajeto) e 9.8 (escola) em tabelas separadas | `NOT_COMPARABLE` (população) |
| Briga/arma | 8.3 "alguém foi fisicamente agredido"; 8.4 arma branca; 8.5 arma de fogo | — | 9.9 "luta física"; 9.11; 9.10 | `NOT_COMPARABLE` (população) |
| Agressão por familiar | 8.6 "adulto da família", 30 dias | — | 9.16 "mãe, pai ou responsável", **12 meses** | `NOT_COMPARABLE` (população e período) |
| Cinto | 8.7 "não usou", veículo dirigido por outra pessoa | — | 9.1 "nunca ou raramente", banco da frente ou de trás | `NOT_COMPARABLE` (população) |
| Escola suspendeu aulas | — | 1.6.2 "pelo menos uma vez", 12 meses | 17.2 coluna Total, 12 meses | `NOT_COMPARABLE` (população) |
| Violência na localidade | — | 1.6.1 área "considerada de risco" | 17.1 "presenciou ou ouviu falar", por tipo | `NOT_COMPARABLE` (população; pergunta distinta) |

Detalhes, evidências e similaridade textual: `data/curated/comparability_catalog.csv` e
`reports/relatorio_comparabilidade.md`.
