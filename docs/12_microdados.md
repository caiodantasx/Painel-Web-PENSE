# Microdados: indicadores recalculados, validação e séries

Gerado por `scripts/report_microdata.py` a partir de `data/curated/microdata_*.csv`.

## Fontes e desenho amostral

| Edição | Arquivo | Estrato | UPA | Peso | Pós-estrato | Não resposta |
|---|---|---|---|---|---|---|
| PeNSE 2009 (9º ano, capitais) | `Base_Pense_Completa_2009.txt` | `CAPITAL` | `CAPITAL+ID` | `PESO_AJU_SEXO` | `—` | A CONFIRMAR (sem código de não resposta no dicionário de 2009) |
| PeNSE 2012 (9º ano) | `pense2012Estudantes.txt` | `ESTRATOGEO` | `ESTRATOGEO+UPA` | `PESO` | `—` | A CONFIRMAR (sem código de não resposta no dicionário de 2012) |
| PeNSE 2015 · Amostra 2 | `PENSE_AMOSTRA2_ALUNO.CSV` | `ESTRATO_EXP` | `ESTRATO_EXP+escola` | `PESO` | `—` | CONFIRMADA (Nota metodológica n. 03; reproduz as tabelas 2.11.x publicadas) |
| PeNSE 2015 · Amostra 1 (9º ano) | `PENSE_AMOSTRA1_ALUNOESCOLA.CSV` | `ESTRATOGEOREG` | `ESTRATOGEOREG+escola` | `PESO` | `—` | OFICIAL (Notas metodológicas n. 02 e 03: denominadores só com respostas válidas) |
| PeNSE 2019 | `PENSE2019_MICRODADOS.csv` | `ESTRATO` | `ESTRATO+ESCOLA` | `PESO_ALUNO_FREQ` | `POSEST` | CONFIRMADA (dicionário 2019: 9 = Sem resposta, -2 = Abandono; reproduz os totais das tabelas 2019 dos Temas 9, 10 e 17) |
| PeNSE 2024 | `PENSE2024_MICRODADOS.csv` | `ESTRATO_EXP` | `ESTRATO_EXP+ESCOLA` | `PESO_ALUNO_FREQ` | `POSEST` | CONFIRMADA (reproduz as tabelas publicadas de 2024) |

O exemplo oficial do IBGE (documentação 2019 e 2024: `svydesign(ids=~ESCOLA, strata=~ESTRATO_EXP, weights=~PESO_INICIAL, nest=TRUE)` + `postStratify(~POSEST)`, domínio `IND_EXPANSAO = 1`) é o desenho implementado; os pesos finais `PESO_ALUNO_FREQ` já são os pós-estratificados.

## Validação contra as tabelas publicadas

Por recorte: **REPRODUZ** (Δ estimativa ≤ 0,05 p.p. e limites do IC ≤ 0,15 p.p.), **PRÓXIMO** (≤ 0,30 p.p.). Indicador **VALIDADO**: nenhum recorte além de 0,30 p.p. e ≥ 95% reproduzindo. 2019 usa critério próprio (Nota técnica 01/2022): totais reproduzindo e nenhum recorte além de 2 p.p.

| Ano | Indicador | Tabela | Iguais | Próximos | Fora | Máx. Δ | Status |
|---|---|---|---|---|---|---|---|
| 2015_A1 | NONO_BRIGA_ARMA_BRANCA | 10.11  | 133/140 | 6 | 0 | 0.138 | VALIDADO |
| 2015_A1 | NONO_CAPACETE_NUNCA_RARAMENTE | 10.4  | 124/140 | 16 | 0 | 0.227 | VALIDADO_COM_RESSALVA |
| 2015_A1 | NONO_CINTO_FRENTE | 10.1  | 127/140 | 13 | 0 | 0.140 | VALIDADO_COM_RESSALVA |
| 2015_A1 | NONO_CINTO_FRENTE_OU_TRAS | 10.3  | 1/140 | 34 | 104 | 2.402 | NAO_VALIDADO |
| 2015_A1 | NONO_CINTO_TRAS | 10.2  | 109/140 | 31 | 0 | 0.265 | VALIDADO_COM_RESSALVA |
| 2015_A1 | NONO_CONDUTOR_ALCOOL | 10.6  | 112/140 | 28 | 0 | 0.198 | VALIDADO_COM_RESSALVA |
| 2015_A1 | NONO_CONDUZIU_VEICULO | 10.5  | 107/140 | 33 | 0 | 0.246 | VALIDADO_COM_RESSALVA |
| 2015_A1 | NONO_ESCOLA_INSEGURA | 10.8  | 137/140 | 2 | 0 | 0.061 | VALIDADO |
| 2015_A1 | NONO_TRAJETO_INSEGURO | 10.7  | 135/140 | 4 | 0 | 0.073 | VALIDADO |
| 2015_A1 | NONO_TRAJETO_OU_ESCOLA | 10.9  | 132/140 | 6 | 0 | 0.091 | VALIDADO_COM_RESSALVA |
| 2015_A2 | BRIGA_ARMA_BRANCA | 2.11.10  | 42/42 | 0 | 0 | 0.000 | VALIDADO |
| 2015_A2 | BRIGA_ARMA_FOGO | 2.11.9  | 42/42 | 0 | 0 | 0.000 | VALIDADO |
| 2015_A2 | CAPACETE_AS_VEZES_OU_MAIS | 2.11.5  | 42/42 | 0 | 0 | 0.000 | VALIDADO |
| 2015_A2 | CINTO_FRENTE | 2.11.4 Banco da frente | 42/42 | 0 | 0 | 0.000 | VALIDADO |
| 2015_A2 | CINTO_NUNCA_RARAMENTE | 2.11.3  | 42/42 | 0 | 0 | 0.000 | VALIDADO |
| 2015_A2 | CINTO_TRAS | 2.11.4 Banco de trás | 42/42 | 0 | 0 | 0.000 | VALIDADO |
| 2015_A2 | CONDUTOR_ALCOOL | 2.11.7  | 42/42 | 0 | 0 | 0.000 | VALIDADO |
| 2015_A2 | CONDUZIU_VEICULO | 2.11.6  | 42/42 | 0 | 0 | 0.000 | VALIDADO |
| 2015_A2 | ESCOLA_INSEGURA | 2.11.2  | 42/42 | 0 | 0 | 0.000 | VALIDADO |
| 2015_A2 | TRAJETO_INSEGURO | 2.11.1  | 42/42 | 0 | 0 | 0.000 | VALIDADO |
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

* **2015 Amostra 2 (tabelas 2.11.x recebidas em 27/10/2026):** estimativas e IC reproduzem as tabelas em todos os recortes, desde que o estrato seja `ESTRATO_EXP` (com `ESTRATOGEOREG`, citado no Quadro 3 da Nota n. 01/2018, só 64,6% dos IC reproduziam). Na Amostra 1 vale o inverso: `ESTRATOGEOREG` reproduz 97,1% dos IC da série oficial.
* **Não resposta harmonizada (IBGE 2022, p. 18, nota 7):** a série usa 'sem resposta' no denominador e exclui o 'abandono'. Em 2015 o código 99 mistura os dois; o abandono é reconstruído (99 sem nenhuma resposta posterior). Com essa regra a Amostra 1 reproduz os valores oficiais de 2015 da série do 9º ano (total das capitais, Δ ≤ 0,05 p.p.). O efeito medido por indicador está em `data/curated/microdata_nonresponse_effect.csv`.
* **2019 — confidencialidade (Nota técnica 01/2022):** idade agregada e sexo/idade suprimidos em 0,3% dos registros (recodificados para 9). Totais de Brasil reproduzem (≤ 0,02 p.p.); como o registro com idade suprimida sai do domínio de 13 a 17 anos, as diferenças aparecem em TODOS os recortes (rede, UF, sexo), não só por sexo. A série do 9º ano (sem filtro de idade) reproduz o total das capitais exatamente.
* **Capacete:** 2015 publicou 'às vezes a sempre'; 2019 e 2024 publicaram 'raramente a sempre' (confirmado pelos microdados). As duas definições são calculadas em todas as edições.
* **Venda de drogas no entorno (17.1):** 2024 acrescenta 'ou usando' à pergunta (dicionários): não comparável.
* **Tabela 9.10.1 de 2019:** linhas de seção com números repetidos (artefato da publicação), tratado (STB004).
* **Tabela oficial 10.3 (cinto, frente ou trás, 9º ano):** regra não reproduzida em 2015 nem 2019 (definição do glossário do IBGE testada em 10 variantes); fora da série e da extensão 2024.
* **Dicionário 2009:** rótulos de `DEP2` invertidos em relação aos dados (`DEPEND_ADM` = PRIVADA tem `DEP2` = 1); usa-se o texto.

## Registro histórico: tentativa com os microdados de 2009, 2012 e 2015 (Amostra 1)

Arquivo de registro (`reports/tentativa_microdados_2009_2012_2015A1.csv`, gerado em sessão anterior, SEM script gerador no projeto — mantido só como histórico). As linhas de 2015 A1 estão **superadas**: a Amostra 1 agora é validada pela pipeline na convenção da série (tabela de validação acima). 2009 e 2012 continuam pendentes; a série usa os **valores oficiais publicados** para 2009–2015.

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

Estatística experimental do IBGE (Estudos e Pesquisas n. 46, 2022). ◇ = 2024 calculado com os microdados (não oficial; mesma regra que reproduz a tabela oficial de 2019). `*` = diferença significativa a 5% em relação à edição anterior. Entre anos publicados, o teste é aproximado (erro-padrão derivado do IC publicado) e nunca recebe o selo 'Diferença significativa a 5%'; na comparação 2019→2024 (microdados), o selo exige decisão metodológica registrada.

| Tabela | Indicador | 2009 | 2012 | 2015 | 2019 | 2024 |
|---|---|---|---|---|---|---|
| 10.1 | Dentre aqueles que andaram no banco da frente como passageiro, que nunca ou raramente usar | — | — | 15,4 | 15,1 | — |
| 10.2 | Dentre aqueles que andaram no banco de trás como passageiro, que nunca ou raramente usaram | — | — | 32,2 | 31,5 | — |
| 10.3 | Dentre aqueles que andaram no banco da frente ou no banco de trás como passageiro, que nun | 25,6 | 23,8 * | 33,4 * | 32,4 | — |
| 10.4 | Dentre aqueles que andaram de motocicleta nos 30 dias anteriores à pesquisa, que nunca ou  | 25,2 | 27,4 * | 18,6 * | 17,9 | — |
| 10.5 | Que conduziram veículo motorizado nos 30 dias anteriores à pesquisa | 18,3 | 22,4 * | 24,6 * | 23,3 | — |
| 10.6 | Que andaram em veículo motorizado nos 30 dias anteriores à pesquisa, cujo condutor havia i | 18,3 | 23,8 * | 25,2 * | 25,7 | — |
| 10.7 | Que não compareceram à escola por falta de segurança no caminho de casa para a escola ou d | 6,3 | 9,0 * | 12,7 * | 12,3 | — |
| 10.8 | Que não compareceram à escola por falta de segurança na escola nos 30 dias anteriores à pe | 5,4 | 8,0 * | 9,3 * | 11,3 * | — |
| 10.9 | Que não compareceram à escola por falta de segurança no caminho de casa para a escola ou d | 8,6 | 12,2 * | 15,7 * | 17,3 | — |
| 10.10 | Que estiveram envolvidos em briga com luta física nos 30 dias anteriores à pesquisa | 12,7 | — | — | 12,7 | 13,4 ◇ |
| 10.11 | Que estiveram envolvidos em briga nos 30 dias anteriores à pesquisa, em que alguma pessoa  | 6,0 | 8,3 * | 8,1 | 4,6 * | — |
| 10.12 | Que foram agredidos por algum adulto da família nos 30 dias anteriores à pesquisa | 9,4 | 11,6 * | 16,0 * | — | — |

## Série harmonizada, Brasil, 13 a 17 anos (estimativa e IC 95%, %)

Valores na convenção da série (2015 difere da tabela publicada pelo efeito da harmonização). `*` = diferença significativa a 5% em relação à edição anterior (IC 95% da diferença não inclui o zero). Na série harmonizada, o selo 'Diferença significativa a 5%' exige, além disso, decisão metodológica registrada aprovando a comparação (`config/microdata/comparability_decisions.csv`); sem decisão registrada, a diferença não recebe esse selo e aparece como 'aguarda decisão'. `*✓` = significativa e com decisão registrada (recebe o selo). Significância não indica relevância prática, causa nem ausência de outras limitações. `†` = ponto fora da série (sem tabela publicada para conferir).

| Indicador | 2015 | 2019 | 2024 | Proposta | Decisão |
|---|---|---|---|---|---|
| Faltaram à escola por falta de segurança no trajeto casa-escola | 13,0 (11,8–14,2) ⊘ | 11,6 (11,1–12,1) | 12,5 (11,8–13,1) *✓ | `COMPARABLE_WITH_CAVEATS` | DECISAO_REGISTRADA |
| Faltaram à escola por falta de segurança na escola | 10,1 (9,2–11,0) ⊘ | 10,8 (10,3–11,2) | 13,7 (13,0–14,3) *✓ | `COMPARABLE_WITH_CAVEATS` | DECISAO_REGISTRADA |
| Nunca ou raramente usaram cinto de segurança (banco da frente ou de trás) | 36,0 (34,0–38,0) | 32,1 (31,3–32,9) *✓ | 33,8 (32,9–34,6) *✓ | `COMPARABLE_WITH_CAVEATS` | DECISAO_REGISTRADA |
| Nunca ou raramente usaram cinto no banco da frente | 19,1 (17,0–21,2) | 17,5 (16,8–18,2) | 19,1 (18,2–19,9) *✓ | `COMPARABLE_WITH_CAVEATS` | DECISAO_REGISTRADA |
| Nunca ou raramente usaram cinto no banco de trás | 33,3 (31,3–35,2) | 30,2 (29,4–30,9) *✓ | 31,2 (30,4–32,0) | `COMPARABLE_WITH_CAVEATS` | DECISAO_REGISTRADA |
| Usaram capacete (de raramente a sempre), dentre os que andaram de motocicleta | 91,2 (89,8–92,6) † | 88,9 (87,8–89,9) | 87,9 (87,1–88,7) | `COMPARABLE_WITH_CAVEATS` | DECISAO_REGISTRADA |
| Usaram capacete às vezes, na maior parte do tempo ou sempre, dentre os que andaram de motocicleta | 83,5 (81,2–85,8) | 80,9 (79,7–82,1) † | 78,3 (77,2–79,4) † | `PENDING_REVIEW` | PROPOSTA_AUTOMATICA |
| Conduziram veículo motorizado | 31,0 (29,4–32,7) | 33,0 (32,3–33,7) *✓ | 34,2 (33,3–35,0) *✓ | `COMPARABLE_WITH_CAVEATS` | DECISAO_REGISTRADA |
| Andaram em veículo cujo condutor tinha ingerido bebida alcoólica | 25,2 (23,8–26,6) | 27,1 (26,5–27,7) *✓ | 27,2 (26,6–27,7) | `COMPARABLE_WITH_CAVEATS` | DECISAO_REGISTRADA |
| Envolveram-se em briga em que alguém usou arma de fogo | 6,3 (5,5–7,1) | 2,9 (2,7–3,1) *✓ | 3,9 (3,6–4,2) *✓ | `COMPARABLE_WITH_CAVEATS` | DECISAO_REGISTRADA |
| Envolveram-se em briga em que alguém usou arma branca | 7,8 (6,9–8,7) | 4,8 (4,5–5,1) *✓ | 5,2 (4,9–5,5) *✓ | `COMPARABLE_WITH_CAVEATS` | DECISAO_REGISTRADA |
| Andaram em veículo cujo condutor usou celular | — | 38,1 (37,4–38,7) | 38,5 (37,8–39,1) | `COMPARABLE_WITH_CAVEATS` | DECISAO_REGISTRADA |
| Envolveram-se em briga com luta física | — | 10,6 (10,2–11,0) | 11,2 (10,8–11,6) *✓ | `COMPARABLE_WITH_CAVEATS` | DECISAO_REGISTRADA |
| Foram agredidos fisicamente pela mãe, pai ou responsável | — | 21,0 (20,5–21,5) | 20,0 (19,5–20,6) *✓ | `COMPARABLE_WITH_CAVEATS` | DECISAO_REGISTRADA |
| Foram agredidos fisicamente por outra pessoa (não mãe, pai ou responsável) | — | 13,2 (12,8–13,7) | 12,5 (12,1–12,9) *✓ | `COMPARABLE_WITH_CAVEATS` | DECISAO_REGISTRADA |
| Sofreram acidente ou agressão | — | 18,2 (17,7–18,7) | 17,3 (16,8–17,8) *✓ | `COMPARABLE_WITH_CAVEATS` | DECISAO_REGISTRADA |
| Alguém tocou, manipulou, beijou ou expôs partes do corpo contra a vontade | — | 14,6 (14,2–15,1) | 18,5 (17,9–19,0) *✓ | `COMPARABLE_WITH_CAVEATS` | DECISAO_REGISTRADA |
| Foram ameaçados, intimidados ou obrigados a ter relação ou ato sexual | — | 6,3 (6,0–6,6) | 8,8 (8,4–9,2) *✓ | `COMPARABLE_WITH_CAVEATS` | DECISAO_REGISTRADA |
| Em escolas cujo diretor presenciou/ouviu falar de assaltos e roubos na localidade | — | 47,5 (44,1–50,8) | 28,4 (24,7–32,1) *✓ | `COMPARABLE_WITH_CAVEATS` | DECISAO_REGISTRADA |
| Em escolas cujo diretor presenciou/ouviu falar de tiros ou tiroteios na localidade | — | 18,1 (15,6–20,7) | 13,6 (10,6–16,6) *✓ | `COMPARABLE_WITH_CAVEATS` | DECISAO_REGISTRADA |
| Em escolas cujo diretor presenciou/ouviu falar de venda de drogas na localidade | — | 49,4 (45,8–53,0) | 38,0 (33,5–42,6) | `NOT_COMPARABLE` | PROPOSTA_AUTOMATICA |
| Em escolas cujo diretor presenciou/ouviu falar de agressão física ou espancamento na localidade | — | 22,7 (19,6–25,8) | 16,7 (13,2–20,2) *✓ | `COMPARABLE_WITH_CAVEATS` | DECISAO_REGISTRADA |
| Em escolas cujo diretor presenciou/ouviu falar de assassinato na localidade | — | 15,5 (13,0–18,1) | 10,7 (7,9–13,5) *✓ | `COMPARABLE_WITH_CAVEATS` | DECISAO_REGISTRADA |
| Em escolas cujo diretor presenciou/ouviu falar de violência sexual na localidade | — | 10,1 (8,3–12,0) | 9,8 (7,7–11,8) | `COMPARABLE_WITH_CAVEATS` | DECISAO_REGISTRADA |
| Em escolas que suspenderam ou interromperam aulas por violência | — | 8,0 (6,0–10,0) | 7,7 (6,4–9,0) | `COMPARABLE_WITH_CAVEATS` | DECISAO_REGISTRADA |

`⊘` = edição fora da série principal por decisão registrada em `config/microdata/series_exclusions.csv` (o valor continua disponível para consulta; não entra em variação nem selo).

### Edições fora da série principal por decisão registrada

* `TRAJETO_INSEGURO` — PENSE_2015_A2: Exclusão PROVISÓRIA de 2015 (Amostra 2) da série principal de TRAJETO_INSEGURO, até resolver a diferença de cobertura escolar. Cobertura: a Amostra 2 de 2015 sorteou turmas do 6º ao 9º ano do ensino fundamental e da 1ª à 3ª série do ensino médio (IBGE 2022, p. 14, nota 3, e p. 15); em 2019 as turmas começam no 7º ano (IBGE 2022, p. 16 · ANO_TURMA); em 2024 o dicionário também começa no 7º ano (ANO_TURMA, código 1). Sensibilidade (Brasil, 13 a 17 anos, regra da série · recorte pelo ano autodeclarado, VB01021 = 1): o 6º ano pesa 2,98% do denominador de 2015; sem ele, 2015 passa de 12,99% para 12,46%, e a variação 2015→2019 passa de -1,39 p.p. [-2,69 a -0,10] (significativa a 5%) para -0,86 p.p. [-2,16 a +0,44] (não significativa). Retirando também os 0,22% de 2019 que se declaram no 6º ano (B01021A = 1), o resultado é o mesmo: -0,89 p.p. [-2,19 a +0,41]. A sensibilidade é o MOTIVO da exclusão provisória e NÃO prova que o valor publicado ou o recalculado de 2015 esteja errado; o recorte por ano autodeclarado é aproximação da cobertura por turma. Valores de 2015 preservados e consultáveis, sem mistura: publicado 13,10% [11,88 a 14,31] (tabela 2.11.1, regra da publicação) e recalculado na regra da série 12,99% [11,80 a 14,19]. (Caio Justino De Andrade, 2026-10-27)
* `ESCOLA_INSEGURA` — PENSE_2015_A2: Exclusão PROVISÓRIA de 2015 (Amostra 2) da série principal de ESCOLA_INSEGURA, pelo mesmo critério já aplicado a TRAJETO_INSEGURO. Cobertura: a Amostra 2 de 2015 incluiu turmas do 6º ano (IBGE 2022, p. 14, nota 3, e p. 15) e 2019/2024 começam no 7º ano (Manual de Instrução 2019, p. 7 e 12 · PeNSE 2024, Notas técnicas, PDF p. 17). Sensibilidade (Brasil, 13 a 17 anos, regra da série · recorte pelo ano autodeclarado): o 6º ano pesa 2.98% do denominador de 2015; 2015 passa de 10.06% para 9.39% sem ele, e a variação 2015→2019 passa de +0.70 [-0.30 a +1.71] p.p. (não significativa a 5%) para +1.38 [+0.40 a +2.35] p.p. (significativa); retirando também quem se declara no 6º ano em 2019: +1.36 [+0.38 a +2.34] p.p. (significativa). A conclusão depende do 6º ano: é o MOTIVO da exclusão provisória e NÃO prova que o valor de 2015 esteja errado. O IBGE recomenda comparar 2024 com 2015 (Amostra 2) para Brasil e Grandes Regiões em nível de pesquisa (PeNSE 2024, Notas técnicas, Quadro 1), recomendação que não testa este efeito de cobertura. Valores de 2015 preservados e consultáveis separadamente. (Caio Justino De Andrade, 2026-10-27)
* `NONO_CINTO_FRENTE` — PENSE_2024: 2024 fora da série principal do 9º ano até haver validação do recorte. A série 2015 (Amostra 1)–2019 é a série oficial do IBGE (Estudos e Pesquisas n. 46, 2022, tabelas 10.x), validada pelo projeto nas duas edições. O IBGE recomenda comparar o 9º ano de 2024 com 2015 (A1) e 2019 (PeNSE 2024, Notas técnicas, Quadro 1), mas não publicou tabela do 9º ano para 2024: o valor de 2024 só tem validação INDIRETA (tabelas de 13 a 17 anos). Continua calculado e consultável em separado, marcado como não validado. (Caio Justino De Andrade, 2026-10-27)
* `NONO_CINTO_TRAS` — PENSE_2024: 2024 fora da série principal do 9º ano até haver validação do recorte. A série 2015 (Amostra 1)–2019 é a série oficial do IBGE (Estudos e Pesquisas n. 46, 2022, tabelas 10.x), validada pelo projeto nas duas edições. O IBGE recomenda comparar o 9º ano de 2024 com 2015 (A1) e 2019 (PeNSE 2024, Notas técnicas, Quadro 1), mas não publicou tabela do 9º ano para 2024: o valor de 2024 só tem validação INDIRETA (tabelas de 13 a 17 anos). Continua calculado e consultável em separado, marcado como não validado. (Caio Justino De Andrade, 2026-10-27)
* `NONO_CAPACETE_NUNCA_RARAMENTE` — PENSE_2024: 2024 fora da série principal do 9º ano até haver validação do recorte. A série 2015 (Amostra 1)–2019 é a série oficial do IBGE (Estudos e Pesquisas n. 46, 2022, tabelas 10.x), validada pelo projeto nas duas edições. O IBGE recomenda comparar o 9º ano de 2024 com 2015 (A1) e 2019 (PeNSE 2024, Notas técnicas, Quadro 1), mas não publicou tabela do 9º ano para 2024: o valor de 2024 só tem validação INDIRETA (tabelas de 13 a 17 anos). Continua calculado e consultável em separado, marcado como não validado. (Caio Justino De Andrade, 2026-10-27)
* `NONO_CONDUZIU_VEICULO` — PENSE_2024: 2024 fora da série principal do 9º ano até haver validação do recorte. A série 2015 (Amostra 1)–2019 é a série oficial do IBGE (Estudos e Pesquisas n. 46, 2022, tabelas 10.x), validada pelo projeto nas duas edições. O IBGE recomenda comparar o 9º ano de 2024 com 2015 (A1) e 2019 (PeNSE 2024, Notas técnicas, Quadro 1), mas não publicou tabela do 9º ano para 2024: o valor de 2024 só tem validação INDIRETA (tabelas de 13 a 17 anos). Continua calculado e consultável em separado, marcado como não validado. (Caio Justino De Andrade, 2026-10-27)
* `NONO_CONDUTOR_ALCOOL` — PENSE_2024: 2024 fora da série principal do 9º ano até haver validação do recorte. A série 2015 (Amostra 1)–2019 é a série oficial do IBGE (Estudos e Pesquisas n. 46, 2022, tabelas 10.x), validada pelo projeto nas duas edições. O IBGE recomenda comparar o 9º ano de 2024 com 2015 (A1) e 2019 (PeNSE 2024, Notas técnicas, Quadro 1), mas não publicou tabela do 9º ano para 2024: o valor de 2024 só tem validação INDIRETA (tabelas de 13 a 17 anos). Continua calculado e consultável em separado, marcado como não validado. (Caio Justino De Andrade, 2026-10-27)
* `NONO_TRAJETO_INSEGURO` — PENSE_2024: 2024 fora da série principal do 9º ano até haver validação do recorte. A série 2015 (Amostra 1)–2019 é a série oficial do IBGE (Estudos e Pesquisas n. 46, 2022, tabelas 10.x), validada pelo projeto nas duas edições. O IBGE recomenda comparar o 9º ano de 2024 com 2015 (A1) e 2019 (PeNSE 2024, Notas técnicas, Quadro 1), mas não publicou tabela do 9º ano para 2024: o valor de 2024 só tem validação INDIRETA (tabelas de 13 a 17 anos). Continua calculado e consultável em separado, marcado como não validado. (Caio Justino De Andrade, 2026-10-27)
* `NONO_ESCOLA_INSEGURA` — PENSE_2024: 2024 fora da série principal do 9º ano até haver validação do recorte. A série 2015 (Amostra 1)–2019 é a série oficial do IBGE (Estudos e Pesquisas n. 46, 2022, tabelas 10.x), validada pelo projeto nas duas edições. O IBGE recomenda comparar o 9º ano de 2024 com 2015 (A1) e 2019 (PeNSE 2024, Notas técnicas, Quadro 1), mas não publicou tabela do 9º ano para 2024: o valor de 2024 só tem validação INDIRETA (tabelas de 13 a 17 anos). Continua calculado e consultável em separado, marcado como não validado. (Caio Justino De Andrade, 2026-10-27)
* `NONO_TRAJETO_OU_ESCOLA` — PENSE_2024: 2024 fora da série principal do 9º ano até haver validação do recorte. A série 2015 (Amostra 1)–2019 é a série oficial do IBGE (Estudos e Pesquisas n. 46, 2022, tabelas 10.x), validada pelo projeto nas duas edições. O IBGE recomenda comparar o 9º ano de 2024 com 2015 (A1) e 2019 (PeNSE 2024, Notas técnicas, Quadro 1), mas não publicou tabela do 9º ano para 2024: o valor de 2024 só tem validação INDIRETA (tabelas de 13 a 17 anos). Continua calculado e consultável em separado, marcado como não validado. (Caio Justino De Andrade, 2026-10-27)
* `NONO_BRIGA_ARMA_BRANCA` — PENSE_2024: 2024 fora da série principal do 9º ano até haver validação do recorte. A série 2015 (Amostra 1)–2019 é a série oficial do IBGE (Estudos e Pesquisas n. 46, 2022, tabelas 10.x), validada pelo projeto nas duas edições. O IBGE recomenda comparar o 9º ano de 2024 com 2015 (A1) e 2019 (PeNSE 2024, Notas técnicas, Quadro 1), mas não publicou tabela do 9º ano para 2024: o valor de 2024 só tem validação INDIRETA (tabelas de 13 a 17 anos). Continua calculado e consultável em separado, marcado como não validado. (Caio Justino De Andrade, 2026-10-27)

## Comparabilidade: proposta automática e decisão do pesquisador

Evidências usadas: mesma variável e códigos; **redação comparada palavra por palavra nos dicionários do IBGE**; mesmo universo; reprodução das tabelas publicadas. Para confirmar ou alterar, registrar em `config/microdata/comparability_decisions.csv`.

* `CAPACETE_AS_VEZES_OU_MAIS` → **PENDING_REVIEW**: Fora da série: só 2015 publicou esta definição; em 2019 e 2024 não há tabela para validar a estimativa. Volta à série apenas com validação documental das três edições e decisão registrada.; fora da série por falta de evidência: 2019 (sem tabela publicada para conferir), 2024 (sem tabela publicada pa
* `ESCOLA_LOCAL_DROGAS` → **NOT_COMPARABLE**: variável muda entre edições ({'PENSE_2019': 'E01P81', 'PENSE_2024': 'E01P81A'}); sufixo novo indica pergunta alterada; redação difere nos dicionários: 2019 → 2024: acrescenta “ou usando”; 2019: Microdados públicos de 2019 com controle de confidencialidade (Nota técnica 01/2022): supressão de sexo/id
* `NONO_CINTO_FRENTE_OU_TRAS` → **PENDING_REVIEW**: fora da série por falta de evidência: 2015 (cálculo não reproduz a tabela publicada), 2019 (cálculo não reproduz a tabela publicada), 2024 (sem tabela publicada para conferir); cálculo NÃO reproduz a tabela publicada em 2015, 2019; A regra da tabela oficial 10.3 não foi reproduzida (calculado 33,2% 

## Efeito medido da harmonização da não resposta (total: Brasil ou conjunto das capitais)

| Indicador | Edição | Sem não resposta | Publicação | Série | Série − publicação (p.p.) |
|---|---|---|---|---|---|
| TRAJETO_INSEGURO | 2015_A2 | 13,1 | 13,1 | 13,0 | -0.10 |
| ESCOLA_INSEGURA | 2015_A2 | 10,1 | 10,1 | 10,1 | -0.08 |
| CINTO_NUNCA_RARAMENTE | 2015_A2 | 36,3 | 36,3 | 36,0 | -0.33 |
| CINTO_FRENTE | 2015_A2 | 19,3 | 19,3 | 19,1 | -0.20 |
| CINTO_TRAS | 2015_A2 | 33,7 | 33,7 | 33,3 | -0.41 |
| CAPACETE_QUALQUER_USO | 2015_A2 | 92,4 | 92,4 | 91,2 | -1.20 |
| CAPACETE_AS_VEZES_OU_MAIS | 2015_A2 | 84,6 | 84,6 | 83,5 | -1.10 |
| CONDUZIU_VEICULO | 2015_A2 | 31,3 | 31,3 | 31,0 | -0.27 |
| CONDUTOR_ALCOOL | 2015_A2 | 25,4 | 25,4 | 25,2 | -0.21 |
| BRIGA_ARMA_FOGO | 2015_A2 | 6,4 | 6,4 | 6,3 | -0.04 |
| BRIGA_ARMA_BRANCA | 2015_A2 | 7,9 | 7,9 | 7,8 | -0.06 |
| NONO_CINTO_FRENTE | 2015_A1 | 19,7 | 19,7 | 19,6 | -0.16 |
| NONO_CINTO_TRAS | 2015_A1 | 30,8 | 30,8 | 30,5 | -0.30 |
| NONO_CINTO_FRENTE_OU_TRAS | 2015_A1 | 33,6 | 33,6 | 33,3 | -0.23 |
| NONO_CAPACETE_NUNCA_RARAMENTE | 2015_A1 | 16,8 | 16,8 | 16,6 | -0.18 |
| NONO_CONDUZIU_VEICULO | 2015_A1 | 32,4 | 32,4 | 32,1 | -0.24 |
| NONO_CONDUTOR_ALCOOL | 2015_A1 | 26,3 | 26,3 | 26,1 | -0.21 |
| NONO_TRAJETO_INSEGURO | 2015_A1 | 11,5 | 11,5 | 11,4 | -0.06 |
| NONO_ESCOLA_INSEGURA | 2015_A1 | 9,5 | 9,5 | 9,4 | -0.06 |
| NONO_TRAJETO_OU_ESCOLA | 2015_A1 | 14,8 | 14,8 | 14,7 | -0.05 |
| NONO_BRIGA_ARMA_BRANCA | 2015_A1 | 7,9 | 7,9 | 7,9 | -0.05 |
