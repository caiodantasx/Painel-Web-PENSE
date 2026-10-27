# Matriz de decisão e registro das propostas aprovadas (27/10/2026)

## O que foi feito
1. **Documentos recebidos (27/10/2026):** questionário do aluno 2019, questionário da escola 2019, Manual de
   Instrução 2019, publicação PeNSE 2024 (liv102266, com Notas técnicas) e dicionários 2019 e 2024. Cada um tem hash
   registrado em `registro_fontes.csv`. Três entraram em `data/reference/`:
   `questionario_pense_2019_aluno.pdf`, `questionario_pense_2019_escola.pdf` e `liv102266_PeNSE_2024_publicacao.pdf`.
   O questionário do aluno 2024 (doc5758) foi **lido** no site do IBGE, mas **não baixado**, porque o sandbox não acessa o
   IBGE. O questionário da escola 2024 não foi recebido.
2. **Matriz dos 36 indicadores** (`matriz_decisao_36_indicadores.csv`, `MATRIZ_DECISAO.md`, gerada por
   `scripts/construir_matriz.py`). As 63 redações de 2015 e 2019 conferem com os questionários originais (texto
   extraído em `txt/`).
3. **Sensibilidade ao 6º ano** para os 11 indicadores com 2015 (Amostra 2): `sensibilidade_6ano_todos.md`, gerada por
   `scripts/sensibilidade_6ano_todos.py`. O método reproduz exatamente o resultado já registrado de TRAJETO_INSEGURO.
   ESCOLA_INSEGURA também não é robusta; os outros 9 são.
4. **Lista de marcação** respondida pelo pesquisador. Foram registradas só as propostas marcadas
   (`scripts/registrar_aprovadas.py`, idempotente).

## Decisões registradas (Caio Justino De Andrade, 2026-10-27)
| Bloco | Indicadores | Série | Exclusão |
|---|---|---|---|
| A | CINTO_NUNCA_RARAMENTE, CINTO_FRENTE, CINTO_TRAS, CONDUZIU_VEICULO, CONDUTOR_ALCOOL, BRIGA_ARMA_FOGO, BRIGA_ARMA_BRANCA | 2015–2019–2024 (2015 só Brasil e Grandes Regiões) | — |
| B | ESCOLA_INSEGURA | 2019–2024 | 2015 (Amostra 2), provisória |
| C | CONDUTOR_CELULAR, BRIGA_LUTA_FISICA, ACIDENTE_OU_AGRESSAO, TOQUE_SEM_CONSENTIMENTO, RELACAO_SEXUAL_FORCADA, CAPACETE_QUALQUER_USO, AGREDIDO_PAIS, AGREDIDO_OUTROS | 2019–2024 | — |
| D | ESCOLA_LOCAL_ASSALTOS, _TIROS, _AGRESSAO, _ASSASSINATO, _VIOLENCIA_SEXUAL, ESCOLA_SUSPENDEU_AULAS | 2019–2024 | — |
| E | 9 indicadores NONO_* da série oficial | 2015 (A1)–2019 | 2024, até haver validação |
| — | TRAJETO_INSEGURO | sem mudança de classificação | texto atualizado |

Todas as decisões são COMPARABLE_WITH_CAVEATS. Cada registro traz a validação contra as tabelas oficiais, a regra de
não resposta, a limitação residual e as fontes. **Aprovar a comparabilidade não transforma uma estimativa em validada.**

**Sem decisão:** ESCOLA_LOCAL_DROGAS (não marcado; a proposta automática continua NOT_COMPARABLE) e os pendentes
NONO_BRIGA_LUTA_FISICA, NONO_CINTO_FRENTE_OU_TRAS e CAPACETE_AS_VEZES_OU_MAIS.

## Resultado
* Estimativas, validações, efeito de não resposta e base aprovada: **idênticos** aos de antes do registro.
* Anos da série: mudaram só ESCOLA_INSEGURA (2015 sai) e os 9 do 9º ano (2024 sai). Os pontos continuam calculados e
  consultáveis, marcados "fora da série principal por decisão registrada".
* Selo "Diferença significativa a 5%": aparece só em indicadores com decisão registrada.
  NONO_BRIGA_LUTA_FISICA, sem decisão, tem 36 diferenças significativas marcadas "aguarda decisão".
* Pipeline `scripts/run_all.py`: código 0. Testes: 224/224 aprovados, nenhum pulado.

## Correções feitas durante a aplicação
* `src/pense/microdata/integrate.py`: a nota da série oficial do 9º ano dizia "regra da tabela oficial não reproduzida"
  também quando 2024 sai por decisão registrada, o que era falso. Agora a nota informa a decisão.
* `tests/test_dashboard_e2e.py`: dois testes supunham indicadores sem decisão com nomes fixos. Agora escolhem pelos
  dados. A regra testada não mudou: sem decisão, não há selo; com 2024 fora da série, não há ponto calculado no gráfico oficial.
* Caminho de evidência da sensibilidade corrigido na matriz. O teste de rastreabilidade
  (`test_every_cited_project_file_exists`) detectou o erro.

## Observações abertas
* `data/reference/PeNSE_2019_publicacao.pdf` é o **Manual de Instrução 2019** (mesmo hash do arquivo recebido), não a
  publicação de 2019. O nome está errado no projeto e em `docs/11`. O arquivo não foi renomeado.
* Regra de não resposta de 2019 e 2024: continua sustentada só pela reprodução das tabelas (lacuna documental).
* Questionário da escola 2024 não recebido. O questionário do aluno 2024 foi lido, mas não arquivado.
* O painel rotula o recorte dos indicadores do 9º ano como "Total (13 a 17 anos)". Esse rótulo vem de antes desta rodada.

## Cópia de segurança
`/home/claude/backup_pense_tcc_2026-10-27_pre_matriz/`: tar.gz conferido (257 arquivos), hashes antes e depois e
saídas `data/curated` anteriores. Os três PDFs de referência e a pasta desta matriz já existiam quando a cópia foi feita.
O backup anterior aos pacotes (`backup_pense_tcc_2026-10-27_pre_pacotes`) é de antes de tudo isso.
