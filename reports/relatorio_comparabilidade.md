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
| ESCOLA_VIOLENCIA_LOCALIDADE_2019_2024 | PENSE_2019__17.1 [Agressão física ou espancamento] | PENSE_2024__17.1 [Agressão física ou espancamento] | COMPARABLE_WITH_CAVEATS | decisão humana (Caio Justino De Andrade, 2026-11-07) | Decisão registrada a pedido explícito do pesquisador em 07/11/2026 ("revise tudo"); texto preparado com assistência de IA (Claude Code), sujeito a revisão. Mesma variável nos dicionários de 2019 e 2024 para 'Agressão física ou espancamento'. Mesmo informante ( |
| ESCOLA_VIOLENCIA_LOCALIDADE_2019_2024 | PENSE_2019__17.1 [Assaltos e roubos a pessoas, residências e comércios] | PENSE_2024__17.1 [Assaltos e roubos a pessoas, residências e comércios] | COMPARABLE_WITH_CAVEATS | decisão humana (Caio Justino De Andrade, 2026-11-07) | Decisão registrada a pedido explícito do pesquisador em 07/11/2026 ("revise tudo"); texto preparado com assistência de IA (Claude Code), sujeito a revisão. Mesma variável nos dicionários de 2019 e 2024 para 'Assaltos e roubos a pessoas, residências e comércios |
| ESCOLA_VIOLENCIA_LOCALIDADE_2019_2024 | PENSE_2019__17.1 [Assassinato] | PENSE_2024__17.1 [Assassinato] | COMPARABLE_WITH_CAVEATS | decisão humana (Caio Justino De Andrade, 2026-11-07) | Decisão registrada a pedido explícito do pesquisador em 07/11/2026 ("revise tudo"); texto preparado com assistência de IA (Claude Code), sujeito a revisão. Mesma variável nos dicionários de 2019 e 2024 para 'Assassinato'. Mesmo informante (diretor ou responsáv |
| ESCOLA_VIOLENCIA_LOCALIDADE_2019_2024 | PENSE_2019__17.1 [Tiros ou tiroteios] | PENSE_2024__17.1 [Tiros ou tiroteios] | COMPARABLE_WITH_CAVEATS | decisão humana (Caio Justino De Andrade, 2026-11-07) | Decisão registrada a pedido explícito do pesquisador em 07/11/2026 ("revise tudo"); texto preparado com assistência de IA (Claude Code), sujeito a revisão. Mesma variável nos dicionários de 2019 e 2024 para 'Tiros ou tiroteios'. Mesmo informante (diretor ou re |
| ESCOLA_VIOLENCIA_LOCALIDADE_2019_2024 | PENSE_2019__17.1 [Venda de drogas] | PENSE_2024__17.1 [Venda de drogas] | NOT_COMPARABLE | decisão humana (Caio Justino De Andrade, 2026-11-07) | Decisão registrada a pedido explícito do pesquisador em 07/11/2026 ("revise tudo"); texto preparado com assistência de IA (Claude Code), sujeito a revisão. Pergunta alterada: 2019 (E01P81) 'alguém vendendo drogas'; 2024 (E01P81A) 'alguém vendendo OU USANDO dro |
| ESCOLA_VIOLENCIA_LOCALIDADE_2019_2024 | PENSE_2019__17.1 [Violência sexual] | PENSE_2024__17.1 [Violência sexual] | COMPARABLE_WITH_CAVEATS | decisão humana (Caio Justino De Andrade, 2026-11-07) | Decisão registrada a pedido explícito do pesquisador em 07/11/2026 ("revise tudo"); texto preparado com assistência de IA (Claude Code), sujeito a revisão. Mesma variável nos dicionários de 2019 e 2024 para 'Violência sexual'. Mesmo informante (diretor ou resp |
| ESCOLA_SUSPENSAO_AULAS_2019_2024 | PENSE_2019__17.2 [geral] | PENSE_2024__17.2 [geral] | COMPARABLE_WITH_CAVEATS | decisão humana (Caio Justino De Andrade, 2026-11-07) | Decisão registrada a pedido explícito do pesquisador em 07/11/2026 ("revise tudo"); texto preparado com assistência de IA (Claude Code), sujeito a revisão. Mesma variável (E01P59A1) e redação em 2019 e 2024; numerador = sim. Mesmo informante (diretor ou respon |
| ESCOLA_VIOLENCIA_FALTOU_TRAJETO_2019_2024 | PENSE_2019__17.3 [Agressão física ou espancamento] | PENSE_2024__17.3 [Agressão física ou espancamento] | COMPARABLE_WITH_CAVEATS | decisão humana (Caio Justino De Andrade, 2026-11-07) | Decisão registrada a pedido explícito do pesquisador em 07/11/2026 ("revise tudo"); texto preparado com assistência de IA (Claude Code), sujeito a revisão. Cruzamento de duas perguntas que não mudaram entre 2019 e 2024: 'Agressão física ou espancamento' na loc |
| ESCOLA_VIOLENCIA_FALTOU_TRAJETO_2019_2024 | PENSE_2019__17.3 [Alguma situação de violência] | PENSE_2024__17.3 [Alguma situação de violência] | NOT_COMPARABLE | decisão humana (Caio Justino De Andrade, 2026-11-07) | Decisão registrada a pedido explícito do pesquisador em 07/11/2026 ("revise tudo"); texto preparado com assistência de IA (Claude Code), sujeito a revisão. 'Alguma situação de violência' depende do item de drogas, cuja pergunta mudou em 2024 ('vendendo ou usan |
| ESCOLA_VIOLENCIA_FALTOU_TRAJETO_2019_2024 | PENSE_2019__17.3 [Assaltos e roubos a pessoas, residências e comércios] | PENSE_2024__17.3 [Assaltos e roubos a pessoas, residências e comércios] | COMPARABLE_WITH_CAVEATS | decisão humana (Caio Justino De Andrade, 2026-11-07) | Decisão registrada a pedido explícito do pesquisador em 07/11/2026 ("revise tudo"); texto preparado com assistência de IA (Claude Code), sujeito a revisão. Cruzamento de duas perguntas que não mudaram entre 2019 e 2024: 'Assaltos e roubos a pessoas, residência |
| ESCOLA_VIOLENCIA_FALTOU_TRAJETO_2019_2024 | PENSE_2019__17.3 [Assassinato] | PENSE_2024__17.3 [Assassinato] | COMPARABLE_WITH_CAVEATS | decisão humana (Caio Justino De Andrade, 2026-11-07) | Decisão registrada a pedido explícito do pesquisador em 07/11/2026 ("revise tudo"); texto preparado com assistência de IA (Claude Code), sujeito a revisão. Cruzamento de duas perguntas que não mudaram entre 2019 e 2024: 'Assassinato' na localidade (diretor, me |
| ESCOLA_VIOLENCIA_FALTOU_TRAJETO_2019_2024 | PENSE_2019__17.3 [Tiros ou tiroteios] | PENSE_2024__17.3 [Tiros ou tiroteios] | COMPARABLE_WITH_CAVEATS | decisão humana (Caio Justino De Andrade, 2026-11-07) | Decisão registrada a pedido explícito do pesquisador em 07/11/2026 ("revise tudo"); texto preparado com assistência de IA (Claude Code), sujeito a revisão. Cruzamento de duas perguntas que não mudaram entre 2019 e 2024: 'Tiros ou tiroteios' na localidade (dire |
| ESCOLA_VIOLENCIA_FALTOU_TRAJETO_2019_2024 | PENSE_2019__17.3 [Venda de drogas] | PENSE_2024__17.3 [Venda de drogas] | NOT_COMPARABLE | decisão humana (Caio Justino De Andrade, 2026-11-07) | Decisão registrada a pedido explícito do pesquisador em 07/11/2026 ("revise tudo"); texto preparado com assistência de IA (Claude Code), sujeito a revisão. 'Venda de drogas' depende do item de drogas, cuja pergunta mudou em 2024 ('vendendo ou usando' em vez de |
| ESCOLA_VIOLENCIA_FALTOU_TRAJETO_2019_2024 | PENSE_2019__17.3 [Violência sexual] | PENSE_2024__17.3 [Violência sexual] | COMPARABLE_WITH_CAVEATS | decisão humana (Caio Justino De Andrade, 2026-11-07) | Decisão registrada a pedido explícito do pesquisador em 07/11/2026 ("revise tudo"); texto preparado com assistência de IA (Claude Code), sujeito a revisão. Cruzamento de duas perguntas que não mudaram entre 2019 e 2024: 'Violência sexual' na localidade (direto |

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
| ESCOLA_VIOLENCIA_LOCALIDADE_2019_2024 | COMPARABLE_WITH_CAVEATS | sim |
| ESCOLA_VIOLENCIA_LOCALIDADE_2019_2024 | COMPARABLE_WITH_CAVEATS | sim |
| ESCOLA_VIOLENCIA_LOCALIDADE_2019_2024 | COMPARABLE_WITH_CAVEATS | sim |
| ESCOLA_VIOLENCIA_LOCALIDADE_2019_2024 | COMPARABLE_WITH_CAVEATS | sim |
| ESCOLA_VIOLENCIA_LOCALIDADE_2019_2024 | NOT_COMPARABLE | não |
| ESCOLA_VIOLENCIA_LOCALIDADE_2019_2024 | COMPARABLE_WITH_CAVEATS | sim |
| ESCOLA_SUSPENSAO_AULAS_2019_2024 | COMPARABLE_WITH_CAVEATS | sim |
| ESCOLA_VIOLENCIA_FALTOU_TRAJETO_2019_2024 | COMPARABLE_WITH_CAVEATS | sim |
| ESCOLA_VIOLENCIA_FALTOU_TRAJETO_2019_2024 | NOT_COMPARABLE | não |
| ESCOLA_VIOLENCIA_FALTOU_TRAJETO_2019_2024 | COMPARABLE_WITH_CAVEATS | sim |
| ESCOLA_VIOLENCIA_FALTOU_TRAJETO_2019_2024 | COMPARABLE_WITH_CAVEATS | sim |
| ESCOLA_VIOLENCIA_FALTOU_TRAJETO_2019_2024 | COMPARABLE_WITH_CAVEATS | sim |
| ESCOLA_VIOLENCIA_FALTOU_TRAJETO_2019_2024 | NOT_COMPARABLE | não |
| ESCOLA_VIOLENCIA_FALTOU_TRAJETO_2019_2024 | COMPARABLE_WITH_CAVEATS | sim |

Pontos de série histórica gerados: **1606**.
