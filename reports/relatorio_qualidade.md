# Relatório de qualidade dos dados

Gerado pela pipeline v2.0.0 em 2026-11-07T20:37:19+00:00 (UTC).

## Resumo

- Arquivos inventariados: **63** (2 duplicados por SHA-256, não reprocessados)
- Abas lidas: **407** — por família: {'PENSE_2015_A1': 4, 'PENSE_2015_A2': 24, 'PENSE_2024_IC': 123, 'PENSE_2024_CV': 123, 'PENSE_MULTIANO': 12, 'PENSE_2009_CAPITAIS': 13, 'PENSE_2019_IC': 107, 'NAO_MAPEADA': 1}
- Observações de estimativa: **52713** (+ 23608 linhas de CV usadas para enriquecer/validar)
- Observações aprovadas para análise (canônicas, sem duplicidade entre tabelas): **49298**
- Duplicidades analíticas (mesmo recorte publicado em mais de uma tabela): 3042
- Itens não interpretados (ver `data/processed/unparsed_report.csv`): 1

### Status de validação das observações

| Status | Observações |
|---|---|
| ERROR | 196 |
| NOT_AVAILABLE | 121 |
| REVIEW_REQUIRED | 56 |
| VALID | 51395 |
| VALID_WITH_WARNINGS | 945 |

### Alertas por severidade

| Severidade | Alertas |
|---|---|
| ERROR | 196 |
| REVIEW | 58 |
| WARNING | 961 |
| INFO | 7817 |

Significado: **ERROR** bloqueia a aprovação; **REVIEW** exige decisão humana; **WARNING** é aprovável com ressalva visível; **INFO** é registro de rastreabilidade. Nenhum valor foi removido ou corrigido.

## Regras executadas

Número de avaliações feitas por regra nesta execução (uma regra com 0 alertas e muitas avaliações é evidência de consistência, não de regra inativa):

| Regra | Avaliações | Alertas |
|---|---|---|
| OUT001 | 35053 | 325 |
| VAL002 | 157780 | 12 |
| VAL003/VAL004 | 52592 | 0 |
| VAL008 | 23573 | 781 |
| VAL009 | 23273 | 0 |
| VAL011 | 52713 | 0 |
| VAL014 | 2440 | 1016 |
| VAL015 | 26307 | 0 |
| VAL019 | 74 | 0 |
| VAL020 | 3042 | 0 |
| VAL010 | 23604 | 0 |
| REF_abas_conferidas | 246 | 0 |
| REF_temas | 3 | 0 |
| REF_titulos_iguais | 246 | 0 |
| QST_perguntas_ligadas | 25719 | 0 |

## Alertas por regra

| Regra | Severidade | Classe | Qtde | Exemplo | Origem do exemplo | Ação recomendada |
|---|---|---|---|---|---|---|
| VAL013 | ERROR | NAO_VALIDADO | 196 | Ano do título difere do ano do rodapé | Tema_02_Situacoes_em_Casa_e_na_Escola_2019_20260615.xls / 2.6.3 / B9 | Conferir a edição correta na publicação. |
| VAL022 | REVIEW | NAO_VALIDADO | 56 | Coluna de dimensão sem categoria em cabeçalho assimétrico | tab801.xls / tab 8.1 / H11 | Consultar a publicação para definir o indicador destas colunas. |
| HDR006 | REVIEW | NAO_VALIDADO | 1 | Cabeçalho assimétrico: há colunas por categoria e colunas por dimensão sem categoria, sem coluna total geral. As colunas por dimensão foram  | tab801.xls / tab 8.1 /  | Consultar a publicação/nota técnica para definir a que indicador se referem as colunas por dimensão. |
| ADP000 | REVIEW | NAO_VALIDADO | 1 | Aba sem adaptador (ambiguidade entre PENSE_2015_A2 e PENSE_2019_IC) | Tema_02_Situacoes_em_Casa_e_na_Escola_2019_20260615.xls / 2.6.1 /  | Criar adaptador para a família ou ajustar a detecção. |
| VAL008 | WARNING | POSSIVEL_VALOR_EXTREMO_LEGITIMO | 781 | CV elevado (31.4% ≥ 30%): baixa precisão | avulsos/Tabelas 17.1.xlsx / 17.1.1 / N16 | Exibir com aviso de baixa precisão; evitar ranqueamentos baseados neste valor. |
| VAL005 | WARNING | POSSIVEL_ANOMALIA | 95 | IC com amplitude zero ([0.0, 0.0]): estimativa sem variabilidade amostral aparente — típico de recortes com pouquíssimas unidades | avulsos/Tabelas 17.1.xlsx / 17.1.3 / N37 | Interpretar com cautela; não usar para comparação sem consultar o CV. |
| VAL014 | WARNING | POSSIVEL_ANOMALIA | 84 | Categorias de distribuição somam 96.23% (< 100%) sem nota explicativa | Tema_17_Seguranca_da_Escola_2019_20260615.xls / 17.2.1 / E14 | Verificar categorias omitidas; não redistribuir proporcionalmente. |
| VAL002N | WARNING | POSSIVEL_ANOMALIA | 1 | Limite inferior do IC publicado abaixo de zero (-0.24729097600628946); IC normal não truncado na publicação. Valor preservado; o gráfico exi | tab805.xls / tab 8.5 / L17 | Citar o IC como publicado; não substituir por 0 na base. |
| VAL024 | INFO | INFORMATIVO | 5740 | Ano lido do cabeçalho/seção (tabela com vários anos) | Serie_9ano_2009_2019_Tema_10_Seguranca_e_Violencias.xls / 10.1 / B11 | Conferir na publicação se as colunas de anos medem o mesmo indicador e universo. |
| VAL014 | INFO | INFORMATIVO | 932 | Categorias somam 99.47%; a nota informa que não-respostas não são apresentadas — a diferença (0.53 p.p.) corresponde a elas | Tabelas 2.14.xlsx / 2.14.1 / K12 | Nenhuma: exibir a nota junto à distribuição; não redistribuir. |
| VAL006 | INFO | INFORMATIVO | 686 | IC truncado no limite do intervalo [0, 100] | Amostra_1_Tema_06_Seguranca_da_Escola.xls / 1.1.6.1 / Q10 | Nenhuma: o IBGE limita o IC ao domínio do percentual; o IC fica assimétrico. |
| OUT001 | INFO | POSSIVEL_VALOR_EXTREMO_LEGITIMO | 325 | Valor incomum entre 27 territórios (z robusto -3.9; mediana 77.27) | Amostra_1_Tema_06_Seguranca_da_Escola.xls / 1.2.6.1 / N29 | Revisar contexto; manter o valor — extremos podem ser legítimos. |
| VAL001 | INFO | INFORMATIVO | 121 | Estimativa publicada como símbolo '-' (Dado numérico igual a zero não resultante de arredondamento) | Amostra_1_Tema_06_Seguranca_da_Escola.xls / 1.1.6.1 / H9 | Nenhuma: valor mantido como indisponível; não converter em zero sem decisão documentada. |
| VAL002F | INFO | INFORMATIVO | 11 | Artefato de ponto flutuante (estimativa = 100.00000000000016); valor preservado sem arredondar | Tabelas 17.2.xlsx / 17.2.2 / E17 | Nenhuma: diferença menor que a tolerância numérica. |
| STB004 | INFO | INFORMATIVO | 2 | Linha de seção com valores repetidos da linha seguinte (artefato da publicação); tratada como seção: '13 a 15 anos' | Tema_09_Seguranca_2019_20260615.xls / 9.10.1 / A18 | Nenhuma: valores da linha de seção repetem a linha seguinte e não foram extraídos. |

Lista completa, com célula de origem e status de revisão: `data/processed/quality_issues.csv`.
