# Matriz de evidências metodológicas

Gerada por `scripts/build_evidence_matrix.py` a partir de `data/curated/microdata_*.csv` e da configuração. Tabela completa (com pergunta, regras de numerador/denominador e ressalvas): `data/curated/methodological_evidence_matrix.csv`.

**Evidência:** DIRETA = o cálculo reproduz a tabela publicada da edição; INDIRETA = a mesma variável reproduz tabelas da edição (declarada em `indicators.toml`), valor calculado e não oficial; AUSENTE = sem tabela para conferir (ponto fora da série); FALHOU = não reproduz.

**Decisão:** nenhuma comparação é aprovada automaticamente. `PROPOSTA_AUTOMATICA` aguarda o pesquisador em `config/microdata/comparability_decisions.csv` (modelo em `comparability_decisions_MODELO.csv`).

| Indicador | Edição | Informante | Validação da estimativa | Estimativa e IC reproduzem | Evidência | Na série | Proposta | Decisão | Efeito harmonização (p.p.) |
|---|---|---|---|---|---|---|---|---|---|
| TRAJETO_INSEGURO | 2015 (2015_A2) | Aluno | VALIDADO: 42/42 recortes reproduzem; máx Δ 0.000 p.p. | 42/42 | DIRETA | não (excluída por decisão registrada; ver limitations) | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | -0.1022 |
| TRAJETO_INSEGURO | 2019 (2019) | Aluno | VALIDADO_COM_RESSALVA: 256/317 recortes reproduzem; máx Δ 0.479 p.p. | 256/317 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| TRAJETO_INSEGURO | 2024 (2024) | Aluno | VALIDADO: 306/317 recortes reproduzem; máx Δ 0.101 p.p. | 306/317 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| ESCOLA_INSEGURA | 2015 (2015_A2) | Aluno | VALIDADO: 42/42 recortes reproduzem; máx Δ 0.000 p.p. | 42/42 | DIRETA | não (excluída por decisão registrada; ver limitations) | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | -0.0829 |
| ESCOLA_INSEGURA | 2019 (2019) | Aluno | VALIDADO_COM_RESSALVA: 256/317 recortes reproduzem; máx Δ 0.489 p.p. | 256/317 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| ESCOLA_INSEGURA | 2024 (2024) | Aluno | VALIDADO: 305/317 recortes reproduzem; máx Δ 0.101 p.p. | 305/317 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| CINTO_NUNCA_RARAMENTE | 2015 (2015_A2) | Aluno | VALIDADO: 42/42 recortes reproduzem; máx Δ 0.000 p.p. | 42/42 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | -0.3303 |
| CINTO_NUNCA_RARAMENTE | 2019 (2019) | Aluno | VALIDADO_COM_RESSALVA: 246/317 recortes reproduzem; máx Δ 0.343 p.p. | 246/317 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| CINTO_NUNCA_RARAMENTE | 2024 (2024) | Aluno | VALIDADO: 304/317 recortes reproduzem; máx Δ 0.194 p.p. | 304/317 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| CINTO_FRENTE | 2015 (2015_A2) | Aluno | VALIDADO: 42/42 recortes reproduzem; máx Δ 0.000 p.p. | 42/42 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | -0.202 |
| CINTO_FRENTE | 2019 (2019) | Aluno | VALIDADO_COM_RESSALVA: 245/317 recortes reproduzem; máx Δ 0.209 p.p. | 245/317 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| CINTO_FRENTE | 2024 (2024) | Aluno | VALIDADO: 309/317 recortes reproduzem; máx Δ 0.119 p.p. | 309/317 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| CINTO_TRAS | 2015 (2015_A2) | Aluno | VALIDADO: 42/42 recortes reproduzem; máx Δ 0.000 p.p. | 42/42 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | -0.4079 |
| CINTO_TRAS | 2019 (2019) | Aluno | VALIDADO_COM_RESSALVA: 244/317 recortes reproduzem; máx Δ 0.281 p.p. | 244/317 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| CINTO_TRAS | 2024 (2024) | Aluno | VALIDADO: 305/317 recortes reproduzem; máx Δ 0.154 p.p. | 305/317 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| CAPACETE_QUALQUER_USO | 2015 (2015_A2) | Aluno | NÃO VALIDADO (sem tabela) | — | AUSENTE | não | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | -1.1977 |
| CAPACETE_QUALQUER_USO | 2019 (2019) | Aluno | VALIDADO_COM_RESSALVA: 276/317 recortes reproduzem; máx Δ 0.382 p.p. | 276/317 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| CAPACETE_QUALQUER_USO | 2024 (2024) | Aluno | VALIDADO: 308/317 recortes reproduzem; máx Δ 0.165 p.p. | 308/317 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| CAPACETE_AS_VEZES_OU_MAIS | 2015 (2015_A2) | Aluno | VALIDADO: 42/42 recortes reproduzem; máx Δ 0.000 p.p. | 42/42 | DIRETA | não | PENDING_REVIEW | PROPOSTA_AUTOMATICA | -1.0967 |
| CAPACETE_AS_VEZES_OU_MAIS | 2019 (2019) | Aluno | NÃO VALIDADO (sem tabela) | — | AUSENTE | não | PENDING_REVIEW | PROPOSTA_AUTOMATICA | 0.0 |
| CAPACETE_AS_VEZES_OU_MAIS | 2024 (2024) | Aluno | NÃO VALIDADO (sem tabela) | — | AUSENTE | não | PENDING_REVIEW | PROPOSTA_AUTOMATICA | 0.0 |
| CONDUZIU_VEICULO | 2015 (2015_A2) | Aluno | VALIDADO: 42/42 recortes reproduzem; máx Δ 0.000 p.p. | 42/42 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | -0.2741 |
| CONDUZIU_VEICULO | 2019 (2019) | Aluno | VALIDADO_COM_RESSALVA: 220/317 recortes reproduzem; máx Δ 0.490 p.p. | 220/317 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| CONDUZIU_VEICULO | 2024 (2024) | Aluno | VALIDADO_COM_RESSALVA: 300/317 recortes reproduzem; máx Δ 0.229 p.p. | 300/317 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| CONDUTOR_ALCOOL | 2015 (2015_A2) | Aluno | VALIDADO: 42/42 recortes reproduzem; máx Δ 0.000 p.p. | 42/42 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | -0.2068 |
| CONDUTOR_ALCOOL | 2019 (2019) | Aluno | VALIDADO_COM_RESSALVA: 228/317 recortes reproduzem; máx Δ 0.474 p.p. | 228/317 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| CONDUTOR_ALCOOL | 2024 (2024) | Aluno | VALIDADO: 309/317 recortes reproduzem; máx Δ 0.210 p.p. | 309/317 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| BRIGA_ARMA_FOGO | 2015 (2015_A2) | Aluno | VALIDADO: 42/42 recortes reproduzem; máx Δ 0.000 p.p. | 42/42 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | -0.0363 |
| BRIGA_ARMA_FOGO | 2019 (2019) | Aluno | VALIDADO_COM_RESSALVA: 289/317 recortes reproduzem; máx Δ 0.248 p.p. | 289/317 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| BRIGA_ARMA_FOGO | 2024 (2024) | Aluno | VALIDADO: 316/317 recortes reproduzem; máx Δ 0.087 p.p. | 316/317 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| BRIGA_ARMA_BRANCA | 2015 (2015_A2) | Aluno | VALIDADO: 42/42 recortes reproduzem; máx Δ 0.000 p.p. | 42/42 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | -0.0639 |
| BRIGA_ARMA_BRANCA | 2019 (2019) | Aluno | VALIDADO_COM_RESSALVA: 284/317 recortes reproduzem; máx Δ 0.310 p.p. | 284/317 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| BRIGA_ARMA_BRANCA | 2024 (2024) | Aluno | VALIDADO: 312/317 recortes reproduzem; máx Δ 0.125 p.p. | 312/317 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| CONDUTOR_CELULAR | 2019 (2019) | Aluno | VALIDADO_COM_RESSALVA: 229/317 recortes reproduzem; máx Δ 0.380 p.p. | 229/317 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| CONDUTOR_CELULAR | 2024 (2024) | Aluno | VALIDADO: 303/317 recortes reproduzem; máx Δ 0.128 p.p. | 303/317 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| BRIGA_LUTA_FISICA | 2019 (2019) | Aluno | VALIDADO_COM_RESSALVA: 248/317 recortes reproduzem; máx Δ 0.244 p.p. | 248/317 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| BRIGA_LUTA_FISICA | 2024 (2024) | Aluno | VALIDADO: 304/317 recortes reproduzem; máx Δ 0.099 p.p. | 304/317 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| AGREDIDO_PAIS | 2019 (2019) | Aluno | VALIDADO_COM_RESSALVA: 238/317 recortes reproduzem; máx Δ 0.418 p.p. | 238/317 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| AGREDIDO_PAIS | 2024 (2024) | Aluno | VALIDADO: 307/317 recortes reproduzem; máx Δ 0.269 p.p. | 307/317 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| AGREDIDO_OUTROS | 2019 (2019) | Aluno | VALIDADO_COM_RESSALVA: 253/317 recortes reproduzem; máx Δ 0.508 p.p. | 253/317 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| AGREDIDO_OUTROS | 2024 (2024) | Aluno | VALIDADO: 311/317 recortes reproduzem; máx Δ 0.072 p.p. | 311/317 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| ACIDENTE_OU_AGRESSAO | 2019 (2019) | Aluno | VALIDADO_COM_RESSALVA: 247/317 recortes reproduzem; máx Δ 0.205 p.p. | 247/317 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| ACIDENTE_OU_AGRESSAO | 2024 (2024) | Aluno | VALIDADO: 306/317 recortes reproduzem; máx Δ 0.118 p.p. | 306/317 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| TOQUE_SEM_CONSENTIMENTO | 2019 (2019) | Aluno | VALIDADO_COM_RESSALVA: 260/317 recortes reproduzem; máx Δ 0.314 p.p. | 260/317 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| TOQUE_SEM_CONSENTIMENTO | 2024 (2024) | Aluno | VALIDADO: 309/317 recortes reproduzem; máx Δ 0.106 p.p. | 309/317 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| RELACAO_SEXUAL_FORCADA | 2019 (2019) | Aluno | VALIDADO_COM_RESSALVA: 275/317 recortes reproduzem; máx Δ 0.246 p.p. | 275/317 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| RELACAO_SEXUAL_FORCADA | 2024 (2024) | Aluno | VALIDADO: 313/317 recortes reproduzem; máx Δ 0.109 p.p. | 313/317 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| ESCOLA_LOCAL_ASSALTOS | 2019 (2019) | Escola (diretor) | VALIDADO_COM_RESSALVA: 53/73 recortes reproduzem; máx Δ 0.182 p.p. | 53/73 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| ESCOLA_LOCAL_ASSALTOS | 2024 (2024) | Escola (diretor) | VALIDADO: 83/85 recortes reproduzem; máx Δ 0.046 p.p. | 83/85 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| ESCOLA_LOCAL_TIROS | 2019 (2019) | Escola (diretor) | VALIDADO_COM_RESSALVA: 56/73 recortes reproduzem; máx Δ 0.288 p.p. | 56/73 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| ESCOLA_LOCAL_TIROS | 2024 (2024) | Escola (diretor) | VALIDADO: 84/85 recortes reproduzem; máx Δ 0.025 p.p. | 84/85 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| ESCOLA_LOCAL_DROGAS | 2019 (2019) | Escola (diretor) | VALIDADO_COM_RESSALVA: 61/73 recortes reproduzem; máx Δ 0.157 p.p. | 61/73 | DIRETA | não | NOT_COMPARABLE | PROPOSTA_AUTOMATICA | 0.0 |
| ESCOLA_LOCAL_DROGAS | 2024 (2024) | Escola (diretor) | VALIDADO: 83/85 recortes reproduzem; máx Δ 0.022 p.p. | 83/85 | DIRETA | não | NOT_COMPARABLE | PROPOSTA_AUTOMATICA | 0.0 |
| ESCOLA_LOCAL_AGRESSAO | 2019 (2019) | Escola (diretor) | VALIDADO_COM_RESSALVA: 59/73 recortes reproduzem; máx Δ 0.271 p.p. | 59/73 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| ESCOLA_LOCAL_AGRESSAO | 2024 (2024) | Escola (diretor) | VALIDADO: 84/85 recortes reproduzem; máx Δ 0.026 p.p. | 84/85 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| ESCOLA_LOCAL_ASSASSINATO | 2019 (2019) | Escola (diretor) | VALIDADO_COM_RESSALVA: 65/73 recortes reproduzem; máx Δ 0.163 p.p. | 65/73 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| ESCOLA_LOCAL_ASSASSINATO | 2024 (2024) | Escola (diretor) | VALIDADO: 84/85 recortes reproduzem; máx Δ 0.045 p.p. | 84/85 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| ESCOLA_LOCAL_VIOLENCIA_SEXUAL | 2019 (2019) | Escola (diretor) | VALIDADO_COM_RESSALVA: 65/73 recortes reproduzem; máx Δ 0.224 p.p. | 65/73 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| ESCOLA_LOCAL_VIOLENCIA_SEXUAL | 2024 (2024) | Escola (diretor) | VALIDADO: 85/85 recortes reproduzem; máx Δ 0.028 p.p. | 85/85 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| ESCOLA_SUSPENDEU_AULAS | 2019 (2019) | Escola (diretor) | VALIDADO_COM_RESSALVA: 68/73 recortes reproduzem; máx Δ 0.187 p.p. | 68/73 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| ESCOLA_SUSPENDEU_AULAS | 2024 (2024) | Escola (diretor) | VALIDADO: 82/85 recortes reproduzem; máx Δ 0.033 p.p. | 82/85 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| NONO_CINTO_FRENTE | 2015 (2015_A1) | Aluno | VALIDADO_COM_RESSALVA: 127/140 recortes reproduzem; máx Δ 0.140 p.p. | 127/140 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | -0.1592 |
| NONO_CINTO_FRENTE | 2019 (2019) | Aluno | VALIDADO_COM_RESSALVA: 130/140 recortes reproduzem; máx Δ 0.935 p.p. | 130/140 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| NONO_CINTO_FRENTE | 2024 (2024) | Aluno | NÃO VALIDADO (sem tabela) | — | INDIRETA | não (excluída por decisão registrada; ver limitations) | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| NONO_CINTO_TRAS | 2015 (2015_A1) | Aluno | VALIDADO_COM_RESSALVA: 109/140 recortes reproduzem; máx Δ 0.265 p.p. | 109/140 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | -0.3034 |
| NONO_CINTO_TRAS | 2019 (2019) | Aluno | VALIDADO_COM_RESSALVA: 127/140 recortes reproduzem; máx Δ 0.502 p.p. | 127/140 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| NONO_CINTO_TRAS | 2024 (2024) | Aluno | NÃO VALIDADO (sem tabela) | — | INDIRETA | não (excluída por decisão registrada; ver limitations) | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| NONO_CINTO_FRENTE_OU_TRAS | 2015 (2015_A1) | Aluno | NAO_VALIDADO: 1/140 recortes reproduzem; máx Δ 2.402 p.p. | 1/140 | FALHOU | não | PENDING_REVIEW | PROPOSTA_AUTOMATICA | -0.2269 |
| NONO_CINTO_FRENTE_OU_TRAS | 2019 (2019) | Aluno | NAO_VALIDADO: 1/140 recortes reproduzem; máx Δ 5.543 p.p. | 1/140 | FALHOU | não | PENDING_REVIEW | PROPOSTA_AUTOMATICA | 0.0 |
| NONO_CINTO_FRENTE_OU_TRAS | 2024 (2024) | Aluno | NÃO VALIDADO (sem tabela) | — | AUSENTE | não | PENDING_REVIEW | PROPOSTA_AUTOMATICA | 0.0 |
| NONO_CAPACETE_NUNCA_RARAMENTE | 2015 (2015_A1) | Aluno | VALIDADO_COM_RESSALVA: 124/140 recortes reproduzem; máx Δ 0.227 p.p. | 124/140 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | -0.1767 |
| NONO_CAPACETE_NUNCA_RARAMENTE | 2019 (2019) | Aluno | VALIDADO_COM_RESSALVA: 131/140 recortes reproduzem; máx Δ 1.716 p.p. | 131/140 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| NONO_CAPACETE_NUNCA_RARAMENTE | 2024 (2024) | Aluno | NÃO VALIDADO (sem tabela) | — | INDIRETA | não (excluída por decisão registrada; ver limitations) | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| NONO_CONDUZIU_VEICULO | 2015 (2015_A1) | Aluno | VALIDADO_COM_RESSALVA: 107/140 recortes reproduzem; máx Δ 0.246 p.p. | 107/140 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | -0.2412 |
| NONO_CONDUZIU_VEICULO | 2019 (2019) | Aluno | VALIDADO_COM_RESSALVA: 126/140 recortes reproduzem; máx Δ 0.421 p.p. | 126/140 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| NONO_CONDUZIU_VEICULO | 2024 (2024) | Aluno | NÃO VALIDADO (sem tabela) | — | INDIRETA | não (excluída por decisão registrada; ver limitations) | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| NONO_CONDUTOR_ALCOOL | 2015 (2015_A1) | Aluno | VALIDADO_COM_RESSALVA: 112/140 recortes reproduzem; máx Δ 0.198 p.p. | 112/140 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | -0.2137 |
| NONO_CONDUTOR_ALCOOL | 2019 (2019) | Aluno | VALIDADO_COM_RESSALVA: 127/140 recortes reproduzem; máx Δ 0.628 p.p. | 127/140 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| NONO_CONDUTOR_ALCOOL | 2024 (2024) | Aluno | NÃO VALIDADO (sem tabela) | — | INDIRETA | não (excluída por decisão registrada; ver limitations) | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| NONO_TRAJETO_INSEGURO | 2015 (2015_A1) | Aluno | VALIDADO: 135/140 recortes reproduzem; máx Δ 0.073 p.p. | 135/140 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | -0.0577 |
| NONO_TRAJETO_INSEGURO | 2019 (2019) | Aluno | VALIDADO_COM_RESSALVA: 129/140 recortes reproduzem; máx Δ 0.607 p.p. | 129/140 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| NONO_TRAJETO_INSEGURO | 2024 (2024) | Aluno | NÃO VALIDADO (sem tabela) | — | INDIRETA | não (excluída por decisão registrada; ver limitations) | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| NONO_ESCOLA_INSEGURA | 2015 (2015_A1) | Aluno | VALIDADO: 137/140 recortes reproduzem; máx Δ 0.061 p.p. | 137/140 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | -0.0551 |
| NONO_ESCOLA_INSEGURA | 2019 (2019) | Aluno | VALIDADO_COM_RESSALVA: 129/140 recortes reproduzem; máx Δ 0.712 p.p. | 129/140 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| NONO_ESCOLA_INSEGURA | 2024 (2024) | Aluno | NÃO VALIDADO (sem tabela) | — | INDIRETA | não (excluída por decisão registrada; ver limitations) | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| NONO_TRAJETO_OU_ESCOLA | 2015 (2015_A1) | Aluno | VALIDADO_COM_RESSALVA: 132/140 recortes reproduzem; máx Δ 0.091 p.p. | 132/140 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | -0.0516 |
| NONO_TRAJETO_OU_ESCOLA | 2019 (2019) | Aluno | VALIDADO_COM_RESSALVA: 125/140 recortes reproduzem; máx Δ 0.668 p.p. | 125/140 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| NONO_TRAJETO_OU_ESCOLA | 2024 (2024) | Aluno | NÃO VALIDADO (sem tabela) | — | INDIRETA | não (excluída por decisão registrada; ver limitations) | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| NONO_BRIGA_LUTA_FISICA | 2019 (2019) | Aluno | VALIDADO_COM_RESSALVA: 129/140 recortes reproduzem; máx Δ 0.373 p.p. | 129/140 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | PROPOSTA_AUTOMATICA | 0.0 |
| NONO_BRIGA_LUTA_FISICA | 2024 (2024) | Aluno | NÃO VALIDADO (sem tabela) | — | INDIRETA | sim | COMPARABLE_WITH_CAVEATS | PROPOSTA_AUTOMATICA | 0.0 |
| NONO_BRIGA_ARMA_BRANCA | 2015 (2015_A1) | Aluno | VALIDADO: 133/140 recortes reproduzem; máx Δ 0.138 p.p. | 133/140 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | -0.053 |
| NONO_BRIGA_ARMA_BRANCA | 2019 (2019) | Aluno | VALIDADO: 135/140 recortes reproduzem; máx Δ 0.231 p.p. | 135/140 | DIRETA | sim | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |
| NONO_BRIGA_ARMA_BRANCA | 2024 (2024) | Aluno | NÃO VALIDADO (sem tabela) | — | INDIRETA | não (excluída por decisão registrada; ver limitations) | COMPARABLE_WITH_CAVEATS | DECISAO_REGISTRADA | 0.0 |

## Dúvidas NÃO resolvidas (sem evidência documental suficiente)

| Item | Situação | Documento necessário |
|---|---|---|
| Tabela 8.1 (PeNSE 2009) | 56 observações em revisão (VAL022/HDR006): colunas por dependência sem categoria | Publicação PeNSE 2009 (notas da tabela 8.1) |
| Símbolo “–” nas tabelas de 2015 (Amostra 1) | 120 células mantidas como indisponíveis (VAL001), nunca convertidas em zero | Convenções da publicação PeNSE 2015 |
| Regra de derivação da tabela oficial 10.3 (cinto, frente ou trás, 9º ano) | Não reproduzida em 2015 nem 2019 (10 variantes testadas); fora da série | Plano tabular específico da análise histórica (IBGE, 2022) ou código de derivação do IBGE |
| Limiares de coeficiente de variação (15% e 30%) | Critério de projeto, sem fonte oficial identificada | Notas técnicas da PeNSE 2024 (seção de precisão), se houver |
