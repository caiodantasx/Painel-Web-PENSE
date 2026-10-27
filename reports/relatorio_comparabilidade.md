# Catálogo de comparabilidade entre edições

Pares candidatos definidos em `config/comparability_candidates.csv`. O status automático é conservador: diferença em atributo essencial → `NOT_COMPARABLE`; ausência de impedimento → `PENDING_REVIEW`. `COMPARABLE` só por decisão humana registrada em `config/comparability_decisions.csv`.

| Conceito | Esquerda | Direita | Status final | Origem da decisão | Diferenças / justificativa |
|---|---|---|---|---|---|
| SUSPENSAO_AULAS_VIOLENCIA | PENSE_2015_A1__1.6.2 [geral] | PENSE_2024__17.2 [geral] | NOT_COMPARABLE | regra automática conservadora | População de referência: 'Escolares do 9º ano do ensino fundamental' × 'Escolares de 13 a 17 anos' |
| VIOLENCIA_LOCALIDADE_ESCOLA | PENSE_2015_A1__1.6.1 [geral] | PENSE_2024__17.1 [Agressão física ou espancamento] | NOT_COMPARABLE | regra automática conservadora | População de referência: 'Escolares do 9º ano do ensino fundamental' × 'Escolares de 13 a 17 anos' |
| VIOLENCIA_LOCALIDADE_ESCOLA | PENSE_2015_A1__1.6.1 [geral] | PENSE_2024__17.1 [Assaltos e roubos a pessoas, residências e comércios] | NOT_COMPARABLE | regra automática conservadora | População de referência: 'Escolares do 9º ano do ensino fundamental' × 'Escolares de 13 a 17 anos' |
| VIOLENCIA_LOCALIDADE_ESCOLA | PENSE_2015_A1__1.6.1 [geral] | PENSE_2024__17.1 [Assassinato] | NOT_COMPARABLE | regra automática conservadora | População de referência: 'Escolares do 9º ano do ensino fundamental' × 'Escolares de 13 a 17 anos' |
| VIOLENCIA_LOCALIDADE_ESCOLA | PENSE_2015_A1__1.6.1 [geral] | PENSE_2024__17.1 [Tiros ou tiroteios] | NOT_COMPARABLE | regra automática conservadora | População de referência: 'Escolares do 9º ano do ensino fundamental' × 'Escolares de 13 a 17 anos' |
| VIOLENCIA_LOCALIDADE_ESCOLA | PENSE_2015_A1__1.6.1 [geral] | PENSE_2024__17.1 [Venda de drogas] | NOT_COMPARABLE | regra automática conservadora | População de referência: 'Escolares do 9º ano do ensino fundamental' × 'Escolares de 13 a 17 anos' |
| VIOLENCIA_LOCALIDADE_ESCOLA | PENSE_2015_A1__1.6.1 [geral] | PENSE_2024__17.1 [Violência sexual] | NOT_COMPARABLE | regra automática conservadora | População de referência: 'Escolares do 9º ano do ensino fundamental' × 'Escolares de 13 a 17 anos' |
| FALTA_INSEGURANCA_TRAJETO | PENSE_2009__8.1 [Trajeto casa-escola] | PENSE_2024__9.7 [geral] | NOT_COMPARABLE | regra automática conservadora | População de referência: 'Escolares do 9º ano do ensino fundamental' × 'Escolares de 13 a 17 anos' |
| FALTA_INSEGURANCA_ESCOLA | PENSE_2009__8.1 [Escola] | PENSE_2024__9.8 [geral] | NOT_COMPARABLE | regra automática conservadora | População de referência: 'Escolares do 9º ano do ensino fundamental' × 'Escolares de 13 a 17 anos' |
| BRIGA_AGRESSAO_FISICA | PENSE_2009__8.3 [geral] | PENSE_2024__9.9 [geral] | NOT_COMPARABLE | regra automática conservadora | População de referência: 'Escolares do 9º ano do ensino fundamental' × 'Escolares de 13 a 17 anos' |
| BRIGA_ARMA_BRANCA | PENSE_2009__8.4 [geral] | PENSE_2024__9.11 [geral] | NOT_COMPARABLE | regra automática conservadora | População de referência: 'Escolares do 9º ano do ensino fundamental' × 'Escolares de 13 a 17 anos' |
| BRIGA_ARMA_FOGO | PENSE_2009__8.5 [geral] | PENSE_2024__9.10 [geral] | NOT_COMPARABLE | regra automática conservadora | População de referência: 'Escolares do 9º ano do ensino fundamental' × 'Escolares de 13 a 17 anos' |
| AGRESSAO_FAMILIAR | PENSE_2009__8.6 [geral] | PENSE_2024__9.16 [geral] | NOT_COMPARABLE | regra automática conservadora | População de referência: 'Escolares do 9º ano do ensino fundamental' × 'Escolares de 13 a 17 anos'; Período de referência: 'últimos 30 dias' × '12 meses anteriores à pesquisa' |
| CINTO_SEGURANCA | PENSE_2009__8.7 [geral] | PENSE_2024__9.1 [geral] | NOT_COMPARABLE | regra automática conservadora | População de referência: 'Escolares do 9º ano do ensino fundamental' × 'Escolares de 13 a 17 anos' |
| CONDUCAO_VEICULO | PENSE_2009__8.8 [geral] | PENSE_2024__9.4 [geral] | NOT_COMPARABLE | regra automática conservadora | População de referência: 'Escolares do 9º ano do ensino fundamental menores de 18 anos' × 'Escolares de 13 a 17 anos' |
| CONDUTOR_ALCOOL | PENSE_2009__8.9 [geral] | PENSE_2024__9.5 [geral] | NOT_COMPARABLE | regra automática conservadora | População de referência: 'Escolares do 9º ano do ensino fundamental' × 'Escolares de 13 a 17 anos' |
| ESCOLA_VIOLENCIA_LOCALIDADE_2019_2024 | PENSE_2019__17.1 [Agressão física ou espancamento] | PENSE_2024__17.1 [Agressão física ou espancamento] | PENDING_REVIEW | regra automática conservadora | Nenhum impedimento encontrado nos atributos extraídos. Exige revisão do texto das perguntas e das notas metodológicas antes de qualquer decisão. |
| ESCOLA_VIOLENCIA_LOCALIDADE_2019_2024 | PENSE_2019__17.1 [Assaltos e roubos a pessoas, residências e comércios] | PENSE_2024__17.1 [Assaltos e roubos a pessoas, residências e comércios] | PENDING_REVIEW | regra automática conservadora | Nenhum impedimento encontrado nos atributos extraídos. Exige revisão do texto das perguntas e das notas metodológicas antes de qualquer decisão. |
| ESCOLA_VIOLENCIA_LOCALIDADE_2019_2024 | PENSE_2019__17.1 [Assassinato] | PENSE_2024__17.1 [Assassinato] | PENDING_REVIEW | regra automática conservadora | Nenhum impedimento encontrado nos atributos extraídos. Exige revisão do texto das perguntas e das notas metodológicas antes de qualquer decisão. |
| ESCOLA_VIOLENCIA_LOCALIDADE_2019_2024 | PENSE_2019__17.1 [Tiros ou tiroteios] | PENSE_2024__17.1 [Tiros ou tiroteios] | PENDING_REVIEW | regra automática conservadora | Nenhum impedimento encontrado nos atributos extraídos. Exige revisão do texto das perguntas e das notas metodológicas antes de qualquer decisão. |
| ESCOLA_VIOLENCIA_LOCALIDADE_2019_2024 | PENSE_2019__17.1 [Venda de drogas] | PENSE_2024__17.1 [Venda de drogas] | PENDING_REVIEW | regra automática conservadora | Nenhum impedimento encontrado nos atributos extraídos. Exige revisão do texto das perguntas e das notas metodológicas antes de qualquer decisão. |
| ESCOLA_VIOLENCIA_LOCALIDADE_2019_2024 | PENSE_2019__17.1 [Violência sexual] | PENSE_2024__17.1 [Violência sexual] | PENDING_REVIEW | regra automática conservadora | Nenhum impedimento encontrado nos atributos extraídos. Exige revisão do texto das perguntas e das notas metodológicas antes de qualquer decisão. |
| ESCOLA_SUSPENSAO_AULAS_2019_2024 | PENSE_2019__17.2 [geral] | PENSE_2024__17.2 [geral] | PENDING_REVIEW | regra automática conservadora | Nenhum impedimento encontrado nos atributos extraídos. Exige revisão do texto das perguntas e das notas metodológicas antes de qualquer decisão. |
| ESCOLA_VIOLENCIA_FALTOU_TRAJETO_2019_2024 | PENSE_2019__17.3 [Agressão física ou espancamento] | PENSE_2024__17.3 [Agressão física ou espancamento] | PENDING_REVIEW | regra automática conservadora | Nenhum impedimento encontrado nos atributos extraídos. Exige revisão do texto das perguntas e das notas metodológicas antes de qualquer decisão. |
| ESCOLA_VIOLENCIA_FALTOU_TRAJETO_2019_2024 | PENSE_2019__17.3 [Alguma situação de violência] | PENSE_2024__17.3 [Alguma situação de violência] | PENDING_REVIEW | regra automática conservadora | Nenhum impedimento encontrado nos atributos extraídos. Exige revisão do texto das perguntas e das notas metodológicas antes de qualquer decisão. |
| ESCOLA_VIOLENCIA_FALTOU_TRAJETO_2019_2024 | PENSE_2019__17.3 [Assaltos e roubos a pessoas, residências e comércios] | PENSE_2024__17.3 [Assaltos e roubos a pessoas, residências e comércios] | PENDING_REVIEW | regra automática conservadora | Nenhum impedimento encontrado nos atributos extraídos. Exige revisão do texto das perguntas e das notas metodológicas antes de qualquer decisão. |
| ESCOLA_VIOLENCIA_FALTOU_TRAJETO_2019_2024 | PENSE_2019__17.3 [Assassinato] | PENSE_2024__17.3 [Assassinato] | PENDING_REVIEW | regra automática conservadora | Nenhum impedimento encontrado nos atributos extraídos. Exige revisão do texto das perguntas e das notas metodológicas antes de qualquer decisão. |
| ESCOLA_VIOLENCIA_FALTOU_TRAJETO_2019_2024 | PENSE_2019__17.3 [Tiros ou tiroteios] | PENSE_2024__17.3 [Tiros ou tiroteios] | PENDING_REVIEW | regra automática conservadora | Nenhum impedimento encontrado nos atributos extraídos. Exige revisão do texto das perguntas e das notas metodológicas antes de qualquer decisão. |
| ESCOLA_VIOLENCIA_FALTOU_TRAJETO_2019_2024 | PENSE_2019__17.3 [Venda de drogas] | PENSE_2024__17.3 [Venda de drogas] | PENDING_REVIEW | regra automática conservadora | Nenhum impedimento encontrado nos atributos extraídos. Exige revisão do texto das perguntas e das notas metodológicas antes de qualquer decisão. |
| ESCOLA_VIOLENCIA_FALTOU_TRAJETO_2019_2024 | PENSE_2019__17.3 [Violência sexual] | PENSE_2024__17.3 [Violência sexual] | PENDING_REVIEW | regra automática conservadora | Nenhum impedimento encontrado nos atributos extraídos. Exige revisão do texto das perguntas e das notas metodológicas antes de qualquer decisão. |

## Inclusão na série histórica

| Conceito | Status | Na série? |
|---|---|---|
| SUSPENSAO_AULAS_VIOLENCIA | NOT_COMPARABLE | não |
| VIOLENCIA_LOCALIDADE_ESCOLA | NOT_COMPARABLE | não |
| VIOLENCIA_LOCALIDADE_ESCOLA | NOT_COMPARABLE | não |
| VIOLENCIA_LOCALIDADE_ESCOLA | NOT_COMPARABLE | não |
| VIOLENCIA_LOCALIDADE_ESCOLA | NOT_COMPARABLE | não |
| VIOLENCIA_LOCALIDADE_ESCOLA | NOT_COMPARABLE | não |
| VIOLENCIA_LOCALIDADE_ESCOLA | NOT_COMPARABLE | não |
| FALTA_INSEGURANCA_TRAJETO | NOT_COMPARABLE | não |
| FALTA_INSEGURANCA_ESCOLA | NOT_COMPARABLE | não |
| BRIGA_AGRESSAO_FISICA | NOT_COMPARABLE | não |
| BRIGA_ARMA_BRANCA | NOT_COMPARABLE | não |
| BRIGA_ARMA_FOGO | NOT_COMPARABLE | não |
| AGRESSAO_FAMILIAR | NOT_COMPARABLE | não |
| CINTO_SEGURANCA | NOT_COMPARABLE | não |
| CONDUCAO_VEICULO | NOT_COMPARABLE | não |
| CONDUTOR_ALCOOL | NOT_COMPARABLE | não |
| ESCOLA_VIOLENCIA_LOCALIDADE_2019_2024 | PENDING_REVIEW | não |
| ESCOLA_VIOLENCIA_LOCALIDADE_2019_2024 | PENDING_REVIEW | não |
| ESCOLA_VIOLENCIA_LOCALIDADE_2019_2024 | PENDING_REVIEW | não |
| ESCOLA_VIOLENCIA_LOCALIDADE_2019_2024 | PENDING_REVIEW | não |
| ESCOLA_VIOLENCIA_LOCALIDADE_2019_2024 | PENDING_REVIEW | não |
| ESCOLA_VIOLENCIA_LOCALIDADE_2019_2024 | PENDING_REVIEW | não |
| ESCOLA_SUSPENSAO_AULAS_2019_2024 | PENDING_REVIEW | não |
| ESCOLA_VIOLENCIA_FALTOU_TRAJETO_2019_2024 | PENDING_REVIEW | não |
| ESCOLA_VIOLENCIA_FALTOU_TRAJETO_2019_2024 | PENDING_REVIEW | não |
| ESCOLA_VIOLENCIA_FALTOU_TRAJETO_2019_2024 | PENDING_REVIEW | não |
| ESCOLA_VIOLENCIA_FALTOU_TRAJETO_2019_2024 | PENDING_REVIEW | não |
| ESCOLA_VIOLENCIA_FALTOU_TRAJETO_2019_2024 | PENDING_REVIEW | não |
| ESCOLA_VIOLENCIA_FALTOU_TRAJETO_2019_2024 | PENDING_REVIEW | não |
| ESCOLA_VIOLENCIA_FALTOU_TRAJETO_2019_2024 | PENDING_REVIEW | não |

Pontos de série histórica gerados: **0**.
