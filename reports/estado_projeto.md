> **Registro histórico** (estado de 26/10/2026, noite). Vários números e conclusões abaixo foram SUPERADOS pela auditoria e pelas correções de 27/10/2026 (2015 Amostra 2 validada, não resposta harmonizada, estrato de 2015, comparabilidade só como proposta). Estado atual: `reports/estado_projeto_2026-10-27.md`.

# Estado do projeto — pipeline v2 (26/10/2026, noite)

Código completo no pacote pense_tcc_v2.zip entregue na conversa (microdados não incluídos:
colocar os arquivos do IBGE em data/microdata/ e rodar scripts/run_all.py). Painel publicado:
https://claude.ai/artifact/3n3AGBiSoV9CASo9oe2gza

## Situação

| Medida | Valor |
|---|---|
| Tabelas publicadas na base | 2009 (capitais), 2015 A1, 2019 (Temas 9 e 17), 2024 (Temas 9 e 17), série oficial 9º ano 2009–2019 (Tema 10) |
| Abas lidas | 263 (famílias: PENSE_2015_A1 4, PENSE_MULTIANO 12, PENSE_2019_IC 78, PENSE_2024_IC 78, PENSE_2024_CV 78, PENSE_2009_CAPITAIS 13) |
| Estimativas publicadas extraídas / aprovadas | 31.744 / 29.840 |
| Pergunta de origem preenchida (dicionários IBGE) | 21.964 estimativas |
| Microdados usados no cálculo | 2015 A2, 2019, 2024 (2009, 2012 e 2015 A1 lidos; regra harmonizada não reproduzida) |
| Estimativas calculadas dos microdados | 28.522 |
| Comparabilidade (microdados) | COMPARABLE_WITH_CAVEATS: 34, NOT_COMPARABLE: 1, PENDING_REVIEW: 1 |
| Testes automatizados | 130 aprovados |

## Microdados: indicadores recalculados, validação e séries

Gerado por `scripts/report_microdata.py` a partir de `data/curated/microdata_*.csv`.

## Fontes e desenho amostral

| Edição | Arquivo | Estrato | UPA | Peso | Pós-estrato | Não resposta |
|---|---|---|---|---|---|---|
| PeNSE 2009 (9º ano, capitais) | `Base_Pense_Completa_2009.txt` | `CAPITAL` | `CAPITAL+ID` | `PESO_AJU_SEXO` | `—` | A CONFIRMAR (sem código de não resposta no dicionário de 2009) |
| PeNSE 2012 (9º ano) | `pense2012Estudantes.txt` | `ESTRATOGEO` | `ESTRATOGEO+UPA` | `PESO` | `—` | A CONFIRMAR (sem código de não resposta no dicionário de 2012) |
| PeNSE 2015 · Amostra 2 | `PENSE_AMOSTRA2_ALUNO.CSV` | `ESTRATOGEOREG` | `ESTRATOGEOREG+escola` | `PESO` | `—` | OFICIAL (Nota metodológica n. 03) |
| PeNSE 2015 · Amostra 1 (9º ano) | `PENSE_AMOSTRA1_ALUNOESCOLA.CSV` | `ESTRATOGEOREG` | `ESTRATOGEOREG+escola` | `PESO` | `—` | OFICIAL (Notas metodológicas n. 02 e 03: denominadores só com respostas válidas) |
| PeNSE 2019 | `PENSE2019_MICRODADOS.csv` | `ESTRATO` | `ESTRATO+ESCOLA` | `PESO_ALUNO_FREQ` | `POSEST` | CONFIRMADA (dicionário 2019: 9 = Sem resposta, -2 = Abandono; reproduz os totais das tabelas 2019 dos Temas 9, 10 e 17) |
| PeNSE 2024 | `PENSE2024_MICRODADOS.csv` | `ESTRATO_EXP` | `ESTRATO_EXP+ESCOLA` | `PESO_ALUNO_FREQ` | `POSEST` | CONFIRMADA (reproduz as tabelas publicadas de 2024) |

O exemplo oficial do IBGE (documentação 2019 e 2024: `svydesign(ids=~ESCOLA, strata=~ESTRATO_EXP, weights=~PESO_INICIAL, nest=TRUE)` + `postStratify(~POSEST)`, domínio `IND_EXPANSAO = 1`) é o desenho implementado; os pesos finais `PESO_ALUNO_FREQ` já são os pós-estratificados.

## Validação contra as tabelas publicadas

Por recorte: **REPRODUZ** (Δ estimativa ≤ 0,05 p.p. e limites do IC ≤ 0,15 p.p.), **PRÓXIMO** (≤ 0,30 p.p.). Indicador **VALIDADO**: nenhum recorte além de 0,30 p.p. e ≥ 95% reproduzindo. 2019 usa critério próprio (Nota técnica 01/2022): totais reproduzindo e nenhum recorte além de 2 p.p.

| Ano | Indicador | Tabela | Iguais | Próximos | Fora | Máx. Δ | Status |
|---|---|---|---|---|---|---|---|
| 2019 | ACIDENTE_OU_AGRESSAO | 9.12  | 247/317 | 70 | 0 | 0.205 | VALIDADO_COM_RESSALVA |
| 2019 | AGREDIDO_OUTROS | 9.17  | 253/317 | 62 | 2 | 0.508 | VALIDADO_COM_RESSALVA |
| 2019 | AGREDIDO_PAIS | 9.16  | 238/317 | 78 | 1 | 0.418 | VALIDADO_COM_RESSALVA |
| 2019 | BRIGA_ARMA_BRANCA | 9.11  | 284/317 | 32 | 1 | 0.310 | VALIDADO_COM_RESSALVA |
| 2019 | BRIGA_ARMA_FOGO | 9.10  | 289/317 | 28 | 0 | 0.248 | VALIDADO_COM_RESSALVA |
| 2019 | BRIGA_LUTA_FISICA | 9.9  | 248/317 | 68 | 0 | 0.244 | VALIDADO_COM_RESSALVA |
| 2019 | CAPACETE_QUALQUER_USO | 9.3  | 276/317 | 34 | 6 | 0.382 | VALIDADO_COM_RESSALVA |
| 2019 | CINTO_FRENTE | 9.2 Banco da frente | 245/317 | 72 | 0 | 0.209 | VALIDADO_COM_RESSALVA |
| 2019 | CINTO_NUNCA_RARAMENTE | 9.1  | 246/317 | 69 | 1 | 0.343 | VALIDADO_COM_RESSALVA |
| 2019 | CINTO_TRAS | 9.2 Banco de trás | 244/317 | 71 | 0 | 0.281 | VALIDADO_COM_RESSALVA |
| 2019 | CONDUTOR_ALCOOL | 9.5  | 228/317 | 87 | 2 | 0.474 | VALIDADO_COM_RESSALVA |
| 2019 | CONDUTOR_CELULAR | 9.6  | 229/317 | 86 | 2 | 0.380 | VALIDADO_COM_RESSALVA |
| 2019 | CONDUZIU_VEICULO | 9.4  | 220/317 | 96 | 1 | 0.490 | VALIDADO_COM_RESSALVA |
| 2019 | ESCOLA_INSEGURA | 9.8  | 256/317 | 59 | 2 | 0.489 | VALIDADO_COM_RESSALVA |
| 2019 | ESCOLA_LOCAL_AGRESSAO | 17.1 Agressão física ou espan | 59/73 | 12 | 0 | 0.271 | VALIDADO_COM_RESSALVA |
| 2019 | ESCOLA_LOCAL_ASSALTOS | 17.1 Assaltos e roubos a pess | 53/73 | 14 | 0 | 0.182 | VALIDADO_COM_RESSALVA |
| 2019 | ESCOLA_LOCAL_ASSASSINATO | 17.1 Assassinato | 65/73 | 8 | 0 | 0.163 | VALIDADO_COM_RESSALVA |
| 2019 | ESCOLA_LOCAL_DROGAS | 17.1 Venda de drogas | 61/73 | 11 | 0 | 0.157 | VALIDADO_COM_RESSALVA |
| 2019 | ESCOLA_LOCAL_TIROS | 17.1 Tiros ou tiroteios | 56/73 | 16 | 0 | 0.288 | VALIDADO_COM_RESSALVA |
| 2019 | ESCOLA_LOCAL_VIOLENCIA_SEXUAL | 17.1 Violência sexual | 65/73 | 5 | 0 | 0.224 | VALIDADO_COM_RESSALVA |
| 2019 | ESCOLA_SUSPENDEU_AULAS | 17.2  | 68/73 | 4 | 0 | 0.187 | VALIDADO_COM_RESSALVA |
| 2019 | NONO_BRIGA_ARMA_BRANCA | 10.11  | 135/140 | 5 | 0 | 0.231 | VALIDADO |
| 2019 | NONO_BRIGA_LUTA_FISICA | 10.10  | 129/140 | 10 | 1 | 0.373 | VALIDADO_COM_RESSALVA |
| 2019 | NONO_CAPACETE_NUNCA_RARAMENTE | 10.4  | 131/140 | 7 | 2 | 1.716 | VALIDADO_COM_RESSALVA |
| 2019 | NONO_CINTO_FRENTE | 10.1  | 130/140 | 6 | 2 | 0.935 | VALIDADO_COM_RESSALVA |
| 2019 | NONO_CINTO_FRENTE_OU_TRAS | 10.3  | 1/140 | 22 | 111 | 5.543 | NAO_VALIDADO |
| 2019 | NONO_CINTO_TRAS | 10.2  | 127/140 | 10 | 3 | 0.502 | VALIDADO_COM_RESSALVA |
| 2019 | NONO_CONDUTOR_ALCOOL | 10.6  | 127/140 | 8 | 5 | 0.628 | VALIDADO_COM_RESSALVA |
| 2019 | NONO_CONDUZIU_VEICULO | 10.5  | 126/140 | 12 | 1 | 0.421 | VALIDADO_COM_RESSALVA |
| 2019 | NONO_ESCOLA_INSEGURA | 10.8  | 129/140 | 6 | 4 | 0.712 | VALIDADO_COM_RESSALVA |
| 2019 | NONO_TRAJETO_INSEGURO | 10.7  | 129/140 | 7 | 4 | 0.607 | VALIDADO_COM_RESSALVA |
| 2019 | NONO_TRAJETO_OU_ESCOLA | 10.9  | 125/140 | 8 | 4 | 0.668 | VALIDADO_COM_RESSALVA |
| 2019 | RELACAO_SEXUAL_FORCADA | 9.21  | 275/317 | 42 | 0 | 0.246 | VALIDADO_COM_RESSALVA |
| 2019 | TOQUE_SEM_CONSENTIMENTO | 9.19  | 260/317 | 56 | 1 | 0.314 | VALIDADO_COM_RESSALVA |
| 2019 | TRAJETO_INSEGURO | 9.7  | 256/317 | 58 | 3 | 0.479 | VALIDADO_COM_RESSALVA |
| 2024 | ACIDENTE_OU_AGRESSAO | 9.12  | 306/317 | 7 | 0 | 0.118 | VALIDADO |
| 2024 | AGREDIDO_OUTROS | 9.17  | 311/317 | 4 | 0 | 0.072 | VALIDADO |
| 2024 | AGREDIDO_PAIS | 9.16  | 307/317 | 7 | 0 | 0.269 | VALIDADO |
| 2024 | BRIGA_ARMA_BRANCA | 9.11  | 312/317 | 5 | 0 | 0.125 | VALIDADO |
| 2024 | BRIGA_ARMA_FOGO | 9.10  | 316/317 | 1 | 0 | 0.087 | VALIDADO |
| 2024 | BRIGA_LUTA_FISICA | 9.9  | 304/317 | 8 | 0 | 0.099 | VALIDADO |
| 2024 | CAPACETE_QUALQUER_USO | 9.3  | 308/317 | 4 | 0 | 0.165 | VALIDADO |
| 2024 | CINTO_FRENTE | 9.2 Banco da frente | 309/317 | 1 | 0 | 0.119 | VALIDADO |
| 2024 | CINTO_NUNCA_RARAMENTE | 9.1  | 304/317 | 8 | 0 | 0.194 | VALIDADO |
| 2024 | CINTO_TRAS | 9.2 Banco de trás | 305/317 | 7 | 0 | 0.154 | VALIDADO |
| 2024 | CONDUTOR_ALCOOL | 9.5  | 309/317 | 7 | 0 | 0.210 | VALIDADO |
| 2024 | CONDUTOR_CELULAR | 9.6  | 303/317 | 8 | 0 | 0.128 | VALIDADO |
| 2024 | CONDUZIU_VEICULO | 9.4  | 300/317 | 9 | 0 | 0.229 | VALIDADO_COM_RESSALVA |
| 2024 | ESCOLA_INSEGURA | 9.8  | 305/317 | 7 | 0 | 0.101 | VALIDADO |
| 2024 | ESCOLA_LOCAL_AGRESSAO | 17.1 Agressão física ou espan | 84/85 | 0 | 0 | 0.026 | VALIDADO |
| 2024 | ESCOLA_LOCAL_ASSALTOS | 17.1 Assaltos e roubos a pess | 83/85 | 0 | 0 | 0.046 | VALIDADO |
| 2024 | ESCOLA_LOCAL_ASSASSINATO | 17.1 Assassinato | 84/85 | 0 | 0 | 0.045 | VALIDADO |
| 2024 | ESCOLA_LOCAL_DROGAS | 17.1 Venda de drogas | 83/85 | 0 | 0 | 0.022 | VALIDADO |
| 2024 | ESCOLA_LOCAL_TIROS | 17.1 Tiros ou tiroteios | 84/85 | 0 | 0 | 0.025 | VALIDADO |
| 2024 | ESCOLA_LOCAL_VIOLENCIA_SEXUAL | 17.1 Violência sexual | 85/85 | 0 | 0 | 0.028 | VALIDADO |
| 2024 | ESCOLA_SUSPENDEU_AULAS | 17.2  | 82/85 | 0 | 0 | 0.033 | VALIDADO |
| 2024 | RELACAO_SEXUAL_FORCADA | 9.21  | 313/317 | 4 | 0 | 0.109 | VALIDADO |
| 2024 | TOQUE_SEM_CONSENTIMENTO | 9.19  | 309/317 | 8 | 0 | 0.106 | VALIDADO |
| 2024 | TRAJETO_INSEGURO | 9.7  | 306/317 | 4 | 0 | 0.101 | VALIDADO |

## Achados

* **2019 — confidencialidade (Nota técnica 01/2022):** idade agregada e sexo/idade suprimidos em 0,3% dos registros (recodificados para 9). Todos os totais de Brasil e capitais reproduzem as tabelas (≤ 0,02 p.p.); as diferenças maiores aparecem em recortes por sexo de capitais pequenas.
* **Capacete:** 2015 publicou 'às vezes a sempre'; 2019 e 2024 publicaram 'raramente a sempre' (confirmado pelos microdados). As duas definições são calculadas em todas as edições.
* **Venda de drogas no entorno (17.1):** 2024 acrescenta 'ou usando' à pergunta (dicionários): não comparável.
* **Tabela 9.10.1 de 2019:** linhas de seção com números repetidos (artefato da publicação), tratado (STB004).
* **Tabela oficial 10.3 (cinto, frente ou trás, 9º ano):** regra não reproduzida pelos microdados de 2019; fora da extensão 2024.
* **Dicionário 2009:** rótulos de `DEP2` invertidos em relação aos dados (`DEPEND_ADM` = PRIVADA tem `DEP2` = 1); usa-se o texto.

## Tentativa: série oficial do 9º ano com os microdados de 2009, 2012 e 2015 (Amostra 1)

Os microdados antigos foram lidos (largura fixa pelos dicionários) e os indicadores recalculados, mas a regra harmonizada do IBGE para esses anos não foi reproduzida de forma consistente. Por isso a série usa os **valores oficiais publicados** para 2009–2015; os microdados entram em 2019 (reproduz) e 2024 (extensão).

| Ano | Indicador | Tabela | Iguais | Fora | Máx. Δ | Status |
|---|---|---|---|---|---|---|
| 2009 | NONO_AGREDIDO_ADULTO_FAMILIA | 10.12 | 0/140 | 16 | 0.54 | NAO_VALIDADO |
| 2009 | NONO_BRIGA_ARMA_BRANCA | 10.11 | 16/140 | 7 | 0.69 | NAO_VALIDADO |
| 2009 | NONO_CAPACETE_NUNCA_RARAMENTE | 10.4 | 0/140 | 137 | 5.26 | NAO_VALIDADO |
| 2009 | NONO_CONDUTOR_ALCOOL | 10.6 | 0/140 | 123 | 1.31 | NAO_VALIDADO |
| 2009 | NONO_CONDUZIU_VEICULO | 10.5 | 1/140 | 101 | 2.20 | NAO_VALIDADO |
| 2009 | NONO_ESCOLA_INSEGURA | 10.8 | 23/140 | 2 | 0.33 | NAO_VALIDADO |
| 2009 | NONO_TRAJETO_INSEGURO | 10.7 | 16/140 | 2 | 0.35 | NAO_VALIDADO |
| 2009 | NONO_TRAJETO_OU_ESCOLA | 10.9 | 50/140 | 0 | 0.26 | VALIDADO_COM_RESSALVA |
| 2012 | NONO_AGREDIDO_ADULTO_FAMILIA | 10.12 | 127/140 | 0 | 0.17 | VALIDADO_COM_RESSALVA |
| 2012 | NONO_BRIGA_ARMA_BRANCA | 10.11 | 131/140 | 0 | 0.16 | VALIDADO_COM_RESSALVA |
| 2012 | NONO_CAPACETE_NUNCA_RARAMENTE | 10.4 | 56/140 | 13 | 0.69 | NAO_VALIDADO |
| 2012 | NONO_CONDUTOR_ALCOOL | 10.6 | 79/140 | 1 | 0.38 | NAO_VALIDADO |
| 2012 | NONO_CONDUZIU_VEICULO | 10.5 | 68/140 | 2 | 0.53 | NAO_VALIDADO |
| 2012 | NONO_ESCOLA_INSEGURA | 10.8 | 124/140 | 0 | 0.12 | VALIDADO_COM_RESSALVA |
| 2012 | NONO_TRAJETO_INSEGURO | 10.7 | 138/140 | 0 | 0.06 | VALIDADO |
| 2012 | NONO_TRAJETO_OU_ESCOLA | 10.9 | 135/140 | 0 | 0.07 | VALIDADO |
| 2015_A1 | NONO_AGREDIDO_ADULTO_FAMILIA | 10.12 | 51/140 | 1 | 0.31 | NAO_VALIDADO |
| 2015_A1 | NONO_BRIGA_ARMA_BRANCA | 10.11 | 96/140 | 0 | 0.19 | VALIDADO_COM_RESSALVA |
| 2015_A1 | NONO_CAPACETE_NUNCA_RARAMENTE | 10.4 | 44/140 | 27 | 1.11 | NAO_VALIDADO |
| 2015_A1 | NONO_CINTO_FRENTE | 10.1 | 54/140 | 4 | 0.46 | NAO_VALIDADO |
| 2015_A1 | NONO_CINTO_TRAS | 10.2 | 24/140 | 42 | 0.96 | NAO_VALIDADO |
| 2015_A1 | NONO_CONDUTOR_ALCOOL | 10.6 | 22/140 | 23 | 0.65 | NAO_VALIDADO |
| 2015_A1 | NONO_CONDUZIU_VEICULO | 10.5 | 36/140 | 21 | 0.75 | NAO_VALIDADO |
| 2015_A1 | NONO_ESCOLA_INSEGURA | 10.8 | 94/140 | 0 | 0.20 | VALIDADO_COM_RESSALVA |
| 2015_A1 | NONO_TRAJETO_INSEGURO | 10.7 | 84/140 | 0 | 0.21 | VALIDADO_COM_RESSALVA |
| 2015_A1 | NONO_TRAJETO_OU_ESCOLA | 10.9 | 90/140 | 0 | 0.22 | VALIDADO_COM_RESSALVA |

## Série oficial do 9º ano, total das capitais (IBGE 2009–2019 + extensão 2024)

◇ = 2024 calculado com os microdados (mesma regra que reproduz a tabela oficial de 2019); `*` = diferença significativa a 5% em relação à edição anterior.

| Tabela | Indicador | 2009 | 2012 | 2015 | 2019 | 2024 |
|---|---|---|---|---|---|---|
| 10.1 | Dentre aqueles que andaram no banco da frente como passageiro, que nunca ou raramente usar | — | — | 15,4 | 15,1 | 15,6 ◇ |
| 10.2 | Dentre aqueles que andaram no banco de trás como passageiro, que nunca ou raramente usaram | — | — | 32,2 | 31,5 | 31,8 ◇ |
| 10.3 | Dentre aqueles que andaram no banco da frente ou no banco de trás como passageiro, que nun | 25,6 | 23,8 * | 33,4 * | 32,4 | — |
| 10.4 | Dentre aqueles que andaram de motocicleta nos 30 dias anteriores à pesquisa, que nunca ou  | 25,2 | 27,4 * | 18,6 * | 17,9 | 19,2 ◇ |
| 10.5 | Que conduziram veículo motorizado nos 30 dias anteriores à pesquisa | 18,3 | 22,4 * | 24,6 * | 23,3 | 24,9 ◇ |
| 10.6 | Que andaram em veículo motorizado nos 30 dias anteriores à pesquisa, cujo condutor havia i | 18,3 | 23,8 * | 25,2 * | 25,7 | 25,3 ◇ |
| 10.7 | Que não compareceram à escola por falta de segurança no caminho de casa para a escola ou d | 6,3 | 9,0 * | 12,7 * | 12,3 | 12,2 ◇ |
| 10.8 | Que não compareceram à escola por falta de segurança na escola nos 30 dias anteriores à pe | 5,4 | 8,0 * | 9,3 * | 11,3 * | 14,0 ◇ * |
| 10.9 | Que não compareceram à escola por falta de segurança no caminho de casa para a escola ou d | 8,6 | 12,2 * | 15,7 * | 17,3 | 19,8 ◇ * |
| 10.10 | Que estiveram envolvidos em briga com luta física nos 30 dias anteriores à pesquisa | 12,7 | — | — | 12,7 | 13,4 ◇ |
| 10.11 | Que estiveram envolvidos em briga nos 30 dias anteriores à pesquisa, em que alguma pessoa  | 6,0 | 8,3 * | 8,1 | 4,6 * | 5,5 ◇ |
| 10.12 | Que foram agredidos por algum adulto da família nos 30 dias anteriores à pesquisa | 9,4 | 11,6 * | 16,0 * | — | — |

## Série harmonizada, Brasil, 13 a 17 anos (estimativa e IC 95%, %)

`*` = diferença em relação à edição anterior significativa a 5% (amostras independentes).

| Indicador | 2015 | 2019 | 2024 | Comparabilidade |
|---|---|---|---|---|
| Faltaram à escola por falta de segurança no trajeto casa-escola | 13,1 (11,8–14,4) | 11,6 (11,1–12,1) * | 12,5 (11,8–13,1) * | `COMPARABLE_WITH_CAVEATS` |
| Faltaram à escola por falta de segurança na escola | 10,1 (9,1–11,2) | 10,8 (10,3–11,2) | 13,7 (13,0–14,3) * | `COMPARABLE_WITH_CAVEATS` |
| Nunca ou raramente usaram cinto de segurança (banco da frente ou de trás) | 36,3 (34,3–38,4) | 32,1 (31,3–32,9) * | 33,8 (32,9–34,6) * | `COMPARABLE_WITH_CAVEATS` |
| Nunca ou raramente usaram cinto no banco da frente | 19,3 (17,2–21,4) | 17,5 (16,8–18,2) | 19,1 (18,2–19,9) * | `COMPARABLE_WITH_CAVEATS` |
| Nunca ou raramente usaram cinto no banco de trás | 33,7 (31,6–35,7) | 30,2 (29,4–30,9) * | 31,2 (30,4–32,0) | `COMPARABLE_WITH_CAVEATS` |
| Usaram capacete (de raramente a sempre), dentre os que andaram de motocicleta | 92,4 (90,9–93,9) | 88,9 (87,8–89,9) * | 87,9 (87,1–88,7) | `COMPARABLE_WITH_CAVEATS` |
| Usaram capacete às vezes, na maior parte do tempo ou sempre, dentre os que andaram de motocicleta | 84,6 (82,1–87,1) | 80,9 (79,7–82,1) * | 78,3 (77,2–79,4) * | `COMPARABLE_WITH_CAVEATS` |
| Conduziram veículo motorizado | 31,3 (29,6–33,0) | 33,0 (32,3–33,7) | 34,2 (33,3–35,0) * | `COMPARABLE_WITH_CAVEATS` |
| Andaram em veículo cujo condutor tinha ingerido bebida alcoólica | 25,4 (24,0–26,8) | 27,1 (26,5–27,7) * | 27,2 (26,6–27,7) | `COMPARABLE_WITH_CAVEATS` |
| Envolveram-se em briga em que alguém usou arma de fogo | 6,4 (5,5–7,2) | 2,9 (2,7–3,1) * | 3,9 (3,6–4,2) * | `COMPARABLE_WITH_CAVEATS` |
| Envolveram-se em briga em que alguém usou arma branca | 7,9 (6,9–8,8) | 4,8 (4,5–5,1) * | 5,2 (4,9–5,5) * | `COMPARABLE_WITH_CAVEATS` |
| Andaram em veículo cujo condutor usou celular | — | 38,1 (37,4–38,7) | 38,5 (37,8–39,1) | `COMPARABLE_WITH_CAVEATS` |
| Envolveram-se em briga com luta física | — | 10,6 (10,2–11,0) | 11,2 (10,8–11,6) * | `COMPARABLE_WITH_CAVEATS` |
| Foram agredidos fisicamente pela mãe, pai ou responsável | — | 21,0 (20,5–21,5) | 20,0 (19,5–20,6) * | `COMPARABLE_WITH_CAVEATS` |
| Foram agredidos fisicamente por outra pessoa (não mãe, pai ou responsável) | — | 13,2 (12,8–13,7) | 12,5 (12,1–12,9) * | `COMPARABLE_WITH_CAVEATS` |
| Sofreram acidente ou agressão | — | 18,2 (17,7–18,7) | 17,3 (16,8–17,8) * | `COMPARABLE_WITH_CAVEATS` |
| Alguém tocou, manipulou, beijou ou expôs partes do corpo contra a vontade | — | 14,6 (14,2–15,1) | 18,5 (17,9–19,0) * | `COMPARABLE_WITH_CAVEATS` |
| Foram ameaçados, intimidados ou obrigados a ter relação ou ato sexual | — | 6,3 (6,0–6,6) | 8,8 (8,4–9,2) * | `COMPARABLE_WITH_CAVEATS` |
| Em escolas cujo diretor presenciou/ouviu falar de assaltos e roubos na localidade | — | 47,5 (44,1–50,8) | 28,4 (24,7–32,1) * | `COMPARABLE_WITH_CAVEATS` |
| Em escolas cujo diretor presenciou/ouviu falar de tiros ou tiroteios na localidade | — | 18,1 (15,6–20,7) | 13,6 (10,6–16,6) * | `COMPARABLE_WITH_CAVEATS` |
| Em escolas cujo diretor presenciou/ouviu falar de venda de drogas na localidade | — | 49,4 (45,8–53,0) | 38,0 (33,5–42,6) | `NOT_COMPARABLE` |
| Em escolas cujo diretor presenciou/ouviu falar de agressão física ou espancamento na localidade | — | 22,7 (19,6–25,8) | 16,7 (13,2–20,2) * | `COMPARABLE_WITH_CAVEATS` |
| Em escolas cujo diretor presenciou/ouviu falar de assassinato na localidade | — | 15,5 (13,0–18,1) | 10,7 (7,9–13,5) * | `COMPARABLE_WITH_CAVEATS` |
| Em escolas cujo diretor presenciou/ouviu falar de violência sexual na localidade | — | 10,1 (8,3–12,0) | 9,8 (7,7–11,8) | `COMPARABLE_WITH_CAVEATS` |
| Em escolas que suspenderam ou interromperam aulas por violência | — | 8,0 (6,0–10,0) | 7,7 (6,4–9,0) | `COMPARABLE_WITH_CAVEATS` |

## Comparabilidade: proposta automática e decisão do pesquisador

Evidências usadas: mesma variável e códigos; **redação comparada palavra por palavra nos dicionários do IBGE**; mesmo universo; reprodução das tabelas publicadas. Para confirmar ou alterar, registrar em `config/microdata/comparability_decisions.csv`.

* `ESCOLA_LOCAL_DROGAS` → **NOT_COMPARABLE**: variável muda entre edições ({'PENSE_2019': 'E01P81', 'PENSE_2024': 'E01P81A'}); sufixo novo indica pergunta alterada; redação difere nos dicionários: 2019 → 2024: acrescenta “ou usando”; 2019: Microdados públicos de 2019 com controle de confidencialidade (Nota técnica 01/2022): supressão de sexo/id
* `NONO_CINTO_FRENTE_OU_TRAS` → **PENDING_REVIEW**: cálculo NÃO reproduz a tabela publicada em 2019; sem tabela publicada para conferir o cálculo em 2024; A regra da tabela oficial 10.3 não foi reproduzida (calculado 33,2% × publicado 32,4% nas capitais em 2019; variantes testadas em docs/12_microdados.md). Mantido fora da série até a regra ser docum


## Documentos de referência do IBGE

Os originais ficam em `data/reference/` (fora de `data/raw/`, para não serem lidos como
tabelas de dados). `python scripts/build_reference.py` extrai deles os CSVs versionados em
`config/reference/`; `python scripts/build_crosswalk.py` gera a correspondência 2015 × 2024.

| Original | Conteúdo | CSV gerado | Uso na pipeline |
|---|---|---|---|
| `Guia_Tabelas_PeNSE_2024_20260525.xlsx` | catálogo oficial: 1.510 abas em 19 temas (nome da aba e título) | `guia_tabelas_pense_2024.csv` | conferência automática das abas e títulos lidos (`REF001`–`REF003`, relatório `data/processed/reference_check_guia_2024.csv`) |
| `questionario_pense_2015_aluno.pdf` (IBGE doc4595) | questionário do aluno 2015: 151 perguntas com variável, número, texto, opções, pulos e filtros | `questionario_pense_2015_aluno.csv` | texto de origem para tabelas 2015 do aluno e evidência de comparabilidade com 2024 |
| — | cruzamento da seção B9 (Segurança) 2015 com as 23 tabelas do Tema 9 de 2024 | `correspondencia_2015_aluno_x_2024_tema9.csv` | candidatos para série histórica; nunca aprova par sozinho |
| `dicionarios/` (2009, 2012, 2015 A1 e A2, 2019, 2024) | dicionários de microdados do IBGE: variável, pergunta, códigos, posição (largura fixa) | `dicionario_<EDIÇÃO>.csv` (`scripts/build_dictionaries.py`) | texto da pergunta de origem, comparação de redação entre edições, leitura de 2009/2012 |
| `dicionarios/Exemplo_calculo_*.txt` | exemplos oficiais de estimação (R `survey`, SAS `SURVEYMEANS`) | — | confirmam o desenho implementado (UPA escola, estrato, pós-estratificação, domínio `IND_EXPANSAO = 1`) |
| `Nota_tecnica_01_2022_confidencialidade_PeNSE2019.pdf` | controle de confidencialidade dos microdados 2019 | — | explica as diferenças em recortes restritos; critério de validação de 2019 |
| `PeNSE_2019_publicacao.pdf` (Manual de Instrução 2019) | desenho amostral (53 estratos geográficos × dependência), CV de dimensionamento 4% | — | metodologia do TCC |
| `Guia_Tabelas_PeNSE_2019_20260615.xls`, `Guia_Tabelas_PeNSE_2009_2019_9ano.xls` | catálogos oficiais das tabelas de 2019 e da série do 9º ano | — | referência |

## Resultado da conferência com o guia 2024

As 156 abas de 2024 lidas (Tema 9: 138; Tema 17: 18) estão todas no guia, nenhuma aba
dos dois temas falta nos arquivos e os 156 títulos extraídos são iguais aos do guia
(comparação sem acentos, espaços e prefixo "Tabela x.y.z -").

## Como o questionário foi lido

O PDF tem duas colunas e usa cores com significado (legenda na página 1): **vermelho** =
questão alterada em relação à edição anterior, **verde** = questão nova, **azul** = pulos,
filtros, críticas e alertas. O extrator usa a cor e a posição reais de cada palavra
(pdfplumber): a cor do código da variável vira `change_vs_previous` (ALTERADA / NOVA /
MANTIDA) e o texto azul vai para `filters_and_checks`. A seção B9 (18 perguntas) foi
conferida contra as páginas 15–17 do PDF e é verificada em `tests/test_reference.py`.

## Ressalvas importantes

* As tabelas de 2015 já processadas (Amostra 1, Tema 6 "Segurança da escola") vêm do
  **questionário da escola**, não deste questionário do aluno; por isso este documento ainda
  não preenche `question_text` dessas observações.
* O questionário de 2015 serve às amostras 1 (9º ano) e 2 (13 a 17 anos); algumas perguntas
  só valem para a amostra tipo 2 (ex.: B09016 é pulada para menores de 13 anos).
* A correspondência 2015 × 2024 é leitura dos textos oficiais: 7 pares de **mesmo conceito
  candidato**, 8 **próximos com diferenças**, 4 **conceitos diferentes** (período ou agressor
  diferentes) e 7 sem correspondente. Todos ficam `A_VALIDAR_PELO_PESQUISADOR` até haver o
  questionário 2024 e tabelas 2015 da Amostra 2.


## Adaptadores por família de tabela — onde está cada informação

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


## Pendências e limites conhecidos

## Exigem revisão humana (decisão do pesquisador)

| # | Pendência | Onde aparece | Como resolver |
|---|---|---|---|
| P1 | Texto das perguntas de origem | `question_text` | **Resolvido em grande parte:** preenchido pelos dicionários de microdados do IBGE para 2009 e 2015 A1 (mapeamento manual em `config/question_map.csv`, conferir) e para as tabelas de 2019, 2024 e da série 9º ano cuja ligação foi comprovada por reprodução numérica. Pendente só para tabelas sem indicador calculado (ex.: 9.13–9.15, 9.18, 9.20, 9.22, 9.23, 17.3) |
| P2 | Tabela 8.1 (2009): a que indicador se referem as colunas por dependência administrativa | 56 observações `REVIEW_REQUIRED` (`VAL022`/`HDR006`) | Conferir a publicação PeNSE 2009; registrar a interpretação no adaptador |
| P3 | Denominador das distribuições condicionais (17.2 "por número de vezes") | `denominator_status = REGRA_DERIVADA_REVISAR` (182 observações) | Confirmar na nota técnica que o denominador é o grupo da coluna "Total" |
| P4 | Informante "escolar" inferido pela ausência de menção à escola no título | `informant_method` | Confirmar no questionário do aluno |
| P5 | Limiar de CV de 30% para "baixa precisão" | `settings.toml` | Não consta do manual de 2019 (que dimensiona a amostra para CV de 4% em P = 50%); conferir a nota técnica da publicação 2024 |
| P6 | Significado do símbolo "-" na tabela de 2015 (zero absoluto × não aplicável) | 116 células `NOT_AVAILABLE` | Conferir as convenções da publicação 2015 antes de qualquer conversão |
| P7 | Códigos IBGE dos municípios das capitais | `territories.csv` (`code_source`) | Conferir com a DTB do IBGE |
| P8 | Comparabilidade 2009/2015 × 2024 | 16 pares `NOT_COMPARABLE` (população) | Buscar tabelas com o mesmo universo: PeNSE 2015 **Amostra 2** (13 a 17 anos) e 2019. A correspondência de perguntas 2015 × 2024 já indica 7 pares de mesmo conceito candidato (ver `11_documentos_de_referencia.md`) |

## Microdados (série harmonizada)

| # | Pendência | Onde aparece | Como resolver |
|---|---|---|---|
| M1 | Confirmar a comparabilidade proposta | `data/curated/microdata_comparability.csv` (24 `COMPARABLE_WITH_CAVEATS` propostos) | Conferir questionários 2015/2019/2024 e registrar em `config/microdata/comparability_decisions.csv` |
| M2 | ~~Regra de não resposta de 2019~~ | resolvido | Dicionário 2019: 9 = Sem resposta, −2 = Abandono; totais das tabelas 2019 reproduzidos |
| M3 | Validar 2015 Amostra 2 contra tabelas publicadas | sem tabela 2.11.x | Baixar as tabelas da Amostra 2 (2015), pasta ftp.ibge.gov.br/pense/2015/xls/ |
| M4 | ~~Venda de drogas (E01P81 × E01P81A)~~ | resolvido | Dicionários: 2024 acrescenta 'ou usando' → não comparável |
| M5 | Regra da tabela oficial 10.3 (cinto frente ou trás, 9º ano) | `NONO_CINTO_FRENTE_OU_TRAS` NAO_VALIDADO | Pedir a especificação ao IBGE (nota da série comparável) |
| M6 | Regra harmonizada de 2009/2012/2015 A1 na série do 9º ano | `reports/tentativa_microdados_2009_2012_2015A1.csv` | Série usa os valores oficiais; reproduzir exigiria a especificação do IBGE |

## Não implementado nesta versão

* Teste com leitor de tela real e avaliação de usabilidade com usuários (requisito do TCC
  — fazer com roteiro SUS ou similar).
* Malha geográfica oficial mais recente direto da API do IBGE (a atual é derivada da malha
  municipal do IBGE via `tbrugz/geodata-br`, CC0; o script aceita outra fonte).
* Leitura de ODS com valores em células repetidas muito longas (limitado a 200 repetições;
  suficiente para tabelas do IBGE).
* Dashboard: o layout aprovado anteriormente não estava no pacote recebido; o painel foi
  construído no estilo Power BI descrito no projeto. Se houver um layout aprovado, os
  componentes podem ser transplantados — toda a lógica de dados está em `app.js`, separada
  do CSS.

## Automático × revisão humana

| Etapa | Automático | Humano |
|---|---|---|
| Ingestão, hash, duplicatas | ✔ | — |
| Reconhecimento de família | ✔ (com evidência) | revisar `ADP000` |
| Extração e rastreabilidade | ✔ | revisar `unparsed_report.csv` |
| Validação | ✔ sinaliza | decidir alertas REVIEW |
| Comparabilidade | ✔ só conclui "não comparável" ou "pendente" | aprovar pares com justificativa |
| Série histórica | ✔ para pares aprovados | — |
