# Auditoria independente do projeto PeNSE — 27/10/2026

Objeto: `pense_tcc_v2.zip` (o `pense_tcc_v2 (2).zip` não veio anexado; é o mesmo pacote entregue em 27/10 às 07:40, 214 arquivos). Extraído numa cópia limpa e conferido idêntico à pasta de trabalho (`diff -r` sem diferenças). **Nenhum arquivo do projeto foi alterado.** Scripts de verificação: `auditoria/scripts/`.

Legenda de evidência: **[R]** reproduzido por mim nesta auditoria · **[A]** lido em arquivo do projeto · **[D]** lido em documento do IBGE.

## Documentos recebidos nesta mensagem

| Arquivo | Situação |
|---|---|
| `liv101955.pdf` — *PeNSE: Análise de indicadores comparáveis dos escolares do 9º ano, Municípios das Capitais 2009/2019* (IBGE, Estudos e Pesquisas n. 46, 2022) | **Novo e decisivo.** Notas técnicas sobre harmonização (p. 18–20), definição do indicador 10.3 (p. 120–122 e glossário), aviso de **estatística experimental** |
| Tema 9 e Tema 17 de 2019, Guia 2019, Amostra 1 Tema 6, Documentação 2024, Nota metodológica 01, microdados 2019/2024/2015 A1 | Idênticos (SHA-256/MD5) a arquivos já recebidos |

---

## A. Diagnóstico executivo

1. **A cadeia planilha → base → painel está íntegra e é determinística.** [R]
   - Execução completa refeita do zero, com microdados extraídos dos ZIPs originais do IBGE: as 40 saídas de dados ficaram idênticas byte a byte às entregues, incluindo `microdata_estimates.csv` (21 MB) e `pense_bundle.json`. Só mudaram carimbos de data e tempos de execução.
   - Os 30.016 valores publicados no painel batem 100% com `observations_validated.csv`.
   - Os 28.522 pontos calculados batem com `microdata_estimates.csv`.
   - Uma amostra de 1.479 células de 39 planilhas, relida com leitor independente, deu 1.476 iguais, 0 divergentes e 3 símbolos.
2. **O projeto não roda numa instalação limpa feita como o README manda.** `numpy` e `pandas` são usados, mas não estão declarados. O resultado é: a coleta dos testes é interrompida e `run_all.py` falha na 1ª etapa. [R]
3. **O risco metodológico principal está na série de 13 a 17 anos (2015–2019–2024).** Os 34 "comparável com ressalvas" são todos propostas automáticas, com zero decisões do pesquisador, e já alimentam a série e o selo "Mudança confirmada" no painel. Isso contradiz o próprio `docs/04` e o `docs/10` ("a regra automática só conclui não comparável ou pendente"). Três defeitos sustentam esse risco:
   - **a) O ponto de 2015 nunca foi validado.** Não há nenhuma linha `PENSE_2015_A2` em `microdata_validation_summary.csv`.
   - **b) A convenção de não resposta muda dentro da série.** Em 2015 o código 99 sai do denominador; em 2019 e 2024 o "sem resposta" entra. O texto "efeito típico < 0,2 p.p." é fixo no código (`series.py:80`), e é falso para 7 dos 11 indicadores: no capacete o efeito é de 1,0–1,2 p.p. Harmonizando, **duas conclusões do total Brasil se invertem**. [R]
   - **c) A ausência de validação não rebaixa o status.** `CAPACETE_AS_VEZES_OU_MAIS` não foi conferido em edição nenhuma e mesmo assim saiu como "comparável". [A]
4. **O documento novo do IBGE resolve a dúvida sobre a convenção correta.** A série oficial separa "sem resposta" (entra no denominador) de "abandono de questionário" (sai) — p. 18, nota 7. Testei a regra nos microdados de 2015 A1: os valores oficiais de 2015 de 8 tabelas 10.x são reproduzidos com no máximo 0,05 p.p. de diferença; antes as diferenças iam de 0,07 a 0,32 p.p. [R][D]
5. **O que tem evidência sólida:**
   - 2024 reproduz as tabelas publicadas.
   - 2019 reproduz os totais. A tolerância para os demais recortes se explica pela Nota técnica 01/2022: registros com idade suprimida saem do domínio de 13 a 17 anos. A documentação, porém, cita outro motivo.
   - A série do 9º ano em 2019 reproduz os totais das capitais com Δ 0,00 p.p.
   - Os indicadores 2019–2024 só precisam da decisão registrada e dos avisos.
   - O indicador 10.3 está corretamente fora da série: 10 variantes testadas, nenhuma reproduz.

## B. Resultado real dos testes (27/10/2026, Python 3.13.17)

| Ambiente | Resultado | Evidência |
|---|---|---|
| 1. venv limpo, só `requirements.txt` (procedimento do README) | **Falha: coleta interrompida, 2 erros** (`ModuleNotFoundError: numpy` em `test_microdata.py` e `test_pipeline_integration.py`, este via `pipeline.py` → `microdata/integrate.py` → `run.py`). `run_all.py`: `CalledProcessError` na 1ª etapa | [R] |
| 2. venv limpo + numpy 2.5.4 + pandas 3.1.0 | **121 aprovados, 0 falhas, 1 pulado** (e2e: playwright ausente), 12,1 s | [R] |
| 3. Python do sistema com playwright 1.63 + Chromium | `test_dashboard_e2e`: **9 aprovados** | [R] |

O total de 130 aprovados registrado em `docs/09` só aparece com dependências não declaradas mais o playwright opcional.

Ressalvas:
- **Testes que não recalculam nada.** `test_2024_microdata_reproduce…` e `test_2019_reproduces…` leem os CSVs já gravados no ZIP; eles passam sem microdados e não detectariam uma regressão no cálculo.
- **Defeito no gerador de `docs/09`.** Com um teste pulado no nível do módulo, ele escreve uma linha vazia ``| `` | 0 | 0 | 1 |``.
- **Os 3 "ERROR" no log** são mensagens esperadas dos testes de ZIP corrompido.

## Reprodutibilidade (tarefa 3)

**Comandos** (2 min 52 s com microdados):
```
pip install -r requirements.txt numpy pandas      # numpy/pandas FALTAM no requirements
python scripts/run_all.py   # run_pipeline → run_microdata → run_pipeline → report_microdata → generate_docs → build_dashboard
python -m pytest
```

**Entradas exigidas:**

| Entrada | Situação |
|---|---|
| `data/raw/` (9 arquivos, no ZIP) | ✔ |
| `config/` | ✔ |
| `data/microdata/<ED>/` (não versionado) | 6 arquivos de 6 ZIPs do IBGE; hashes registrados em `auditoria/scripts/extract_micro.py` |
| 2009 | **Passo manual não documentado:** o original se chama `Base_Pense Completa_2009.txt` (com espaço) e a configuração espera `Base_Pense_Completa_2009.txt` |
| README | Só documenta 2015 A2, 2019 e 2024; omite 2009, 2012 e 2015 A1 |

**Saídas:** camadas `staging` → `processed` → `curated` → `dashboard/data`, mais `reports/` e `docs/12`. Todas são regeneradas, **exceto** `reports/tentativa_microdados_2009_2012_2015A1.csv`: não existe script que o produza (resultado sem código).

**Determinismo:** duas execuções produzem saídas de dados idênticas. [R]

## C. Matriz de riscos e pendências

Severidade: **B** = bloqueador (pode alterar resultado do TCC ou impede reprodução) · **I** = importante · **O** = opcional.

| # | Risco / pendência | Altera resultados? | Evidência (arquivo · procedimento) | Sev. |
|---|---|---|---|---|
| R1 | numpy/pandas não declarados | Impede reprodução | `requirements.txt`, `pyproject.toml`; teste em venv limpo | **B** |
| R2 | Convenção de não resposta diferente entre 2015 e 2019/2024 na série; texto fixo "< 0,2 p.p." | **Sim**: Δ até 1,2 p.p.; `CAPACETE_AS_VEZES_OU_MAIS` passa de "confirmada" a "acaso" e `CONDUZIU_VEICULO` o inverso (total Brasil) | `series.py:80`; `scripts/nr_effect.py` | **B** |
| R3 | Ponto de 2015 (Amostra 2) sem validação contra tabela publicada | Sim (11 indicadores) | `microdata_validation_summary.csv` sem linhas A2; `docs/10` M3 | **B** |
| R4 | Comparabilidade automática vira série e "Mudança confirmada" sem decisão humana | Sim (apresentação) | `comparability_decisions.csv` vazio; `series.py` `build_series`; `app.js:995,1034`; contradiz `docs/04` e `docs/10` | **B** |
| R5 | Falta de validação e mudança de categorias não rebaixam o status; o docstring promete PENDING para regra de não resposta não confirmada, e o código não faz | Sim | `series.py:13–17` × `:94–104` | **B** |
| R6 | Série 9º ano 2009–2019 é "estatística experimental" (IBGE); o painel não informa | Interpretação | `liv101955.pdf`, páginas iniciais (verso da folha de rosto) e 4ª capa; `grep experiment` sem resultado | I |
| R7 | 10.3 não reproduzido | Não (já está fora) | 10 variantes testadas, a mais próxima a 0,63 p.p. (`t103.py`) | I |
| R8 | Limiar de CV: 30% sem fonte; 15% fixo no JS, sem fonte nem configuração | Classificação "precisão" | `settings.toml:24`; `app.js:128`; nenhum documento disponível define o limiar | I |
| R9 | Informante só "inferido" em 26.700 observações; pergunta sem fonte em 9.180 (31%) | Metadado | `pense_observations_approved.csv` | I |
| R10 | Estrato de 2015: `ESTRATOGEOREG` (5 estratos em A2, Nota 01/2018) × `ESTRATO_EXP` (56; publicação 2022, Quadro 2) | IC de 2015: erro-padrão 4–7% maior | `strata2015.py` | I |
| R11 | Tolerância de 2 p.p. em 2019: o mecanismo real é idade suprimida → fora do domínio 13–17 (atinge rede e totais), não "recortes por sexo de capitais pequenas" | Justificativa | 19% dos recortes por rede acima de 0,05 p.p.; 9º ano sem filtro de idade reproduz | I |
| R12 | Comparador não confere categorias de resposta (cód. 5 "na maior parte do tempo" → "na maioria das vezes" em cinto e capacete) | Baixo | dicionários 2015 A2/2019/2024 | I |
| R13 | Testes de validação leem saídas gravadas, sem recálculo | Detecção de regressão | `tests/test_microdata.py:88–113` | I |
| R14 | Artefato sem gerador (tentativa 2009/2012/2015 A1) e passo manual do arquivo de 2009 | Reprodutibilidade | `reports/`; `editions.toml:21` | I |
| R15 | Documentação desatualizada ou contraditória (lista abaixo) | Credibilidade | `grep` dirigido | I |
| R16 | P2 (tabela 8.1/2009, 56 em revisão), P3 (denominador derivado em **312** observações; o `docs/10` diz 182), P6 ("-" em **120** células; o `docs/10` diz 116) | Pontual | `relatorio_qualidade.md` | I |
| R17 | Testes entre anos oficiais usam erro-padrão aproximado pelo IC publicado; o IBGE usa regressão logística para tendência; comparações múltiplas | Interpretação | `integrate.py`; `liv101955.pdf` p. 18–21 | O |
| R18 | `.ruff_cache` no ZIP; arquivos de referência com prefixo de hash (`1bf5372a-…`) | Não | listagem do ZIP | O |

**Contradições e afirmações sem evidência (tarefa 4):**

| Documento | Diz | Realidade |
|---|---|---|
| `docs/04`, `docs/10`, `reports/estado_*` | "comparabilidade automática só conclui não comparável/pendente" | Microdados propõem 34 COMPARABLE_WITH_CAVEATS que alimentam a série |
| `docs/10` M1, `estado_projeto.md:432` | 24 propostos | 34 |
| `series.py:80` | "efeito típico < 0,2 p.p." | Medido: 0,02–1,20 p.p. |
| `editions.toml:7–16` | "não recebemos os dicionários"; "2019: 9 PENDENTE" | Dicionários presentes; a linha 139 diz CONFIRMADA |
| `indicators.toml` (13 entradas) | "PENDENTE — questionário 2019/2024 não recebido" | Os dicionários trazem o texto (o painel já usa) |
| `indicators.toml:287` | "2019 reproduz a série oficial exatamente" | Exato só no total das capitais; recortes até 1,72 p.p. (10.4) |
| `README` | "cerca de 15 mil observações"; lista de arquivos e de microdados | 31.744 extraídas; faltam 2019 Tema 9, série 9º ano, microdados 2009/2012/2015 A1 |
| `docs/12` (achado 2019) | diferenças "em recortes por sexo de capitais pequenas" | Também por rede e totais de UF (efeito da idade suprimida) |
| `estado_projeto.md:18` | "130 aprovados" | Só com dependências não declaradas |

## D. Avaliação da série histórica

Status usados: **REPRODUZ** (Δ ≤ 0,05 p.p.) · **PRÓXIMO** (≤ 0,30) · **NÃO VALIDADO** · **PENDENTE**.

Características comuns aos 11 indicadores 2015–2019–2024:

| Dimensão | O que vale para todos |
|---|---|
| População | Escolares de 13 a 17 anos. 2015 A2 usa idade simples (VB01003); 2019 e 2024 usam faixa agregada (códigos 2 e 3) — mesma cobertura |
| Território | 2015 A2 só representa Brasil e Grandes Regiões |
| Desenho | 2015 sem pós-estratificação |
| Evidência por edição | 2019 VALIDADO_COM_RESSALVA, com totais Brasil reproduzidos (Δ ≤ 0,02 p.p.); 2024 VALIDADO; 2015 sem tabela |
| Não resposta | 2015: 99 = "não informado" (mistura sem resposta e abandono), fora do denominador. 2019: 9 = sem resposta (entra), −2 = abandono (sai). 2024: −9 entra, −2 sai |

| Indicador | Pergunta (dicionários) | Num / den | Diferenças metodológicas | Efeito da não resposta (2015 / 2019 / 2024) | Recomendação |
|---|---|---|---|---|---|
| TRAJETO_INSEGURO (B09001) | Idêntica | 2–6 / 1–6 | Só não resposta | 0,10 / 0,09 / 0,09 | 2019–24: comparável c/ ressalvas. 2015: **pendente** até harmonizar e validar a A2 |
| ESCOLA_INSEGURA (B09002) | Idêntica | 2–6 / 1–6 | Idem | 0,08 / 0,09 / 0,11 | Idem |
| BRIGA_ARMA_FOGO (B09004) | Idêntica | 1 / 1–2 | Idem | 0,04 / 0,02 / 0,02 | Idem |
| BRIGA_ARMA_BRANCA (B09005) | Idêntica | 1 / 1–2 | Idem | 0,06 / 0,03 / 0,04 | Idem |
| CINTO_FRENTE (B09006A1) | Idêntica | 2–3 / 2–6 | Rótulo do cód. 5 muda; exclui quem não andou (cód. 1) | 0,20 / 0,15 / 0,17 | 2015 pendente |
| CINTO_TRAS (B09006A2) | Idêntica | 2–3 / 2–6 | Idem | 0,41 / 0,31 / 0,31 | 2015 pendente |
| CINTO_NUNCA_RARAMENTE (frente OU trás) | Idênticas | regra "qualquer" | O 9.1 reproduz em 2019/2024, mas o 10.3 (9º ano) não: regra do IBGE não totalmente conhecida | 0,33 / 0,24 / 0,25 | 2015 pendente; citar a ressalva do 10.3 |
| CAPACETE_QUALQUER_USO (B09007A, 3–6) | "motocicleta" → "motocicleta/moto" | 3–6 / 2–6 | 2015 **publicou outra definição** (4–6); esta nunca foi conferida para 2015 | **1,20 / 1,07 / 1,02** | 2019–24 comparável c/ ressalvas; **2015 pendente** |
| CAPACETE_AS_VEZES_OU_MAIS (4–6) | Idem | 4–6 / 2–6 | **Sem validação em nenhuma edição** (2019/2024 publicaram a outra definição) | 1,10 / 0,98 / 0,91 | **Pendente de revisão**; tirar da série até validar a A2 |
| CONDUZIU_VEICULO (B09008) | Sinônimo "moto" | 2–5 / 1–5 | Conclusão 2015→19 se inverte ao harmonizar | 0,27 / 0,26 / 0,25 | 2015 pendente |
| CONDUTOR_ALCOOL (B09009) | Idêntica | 2–5 / 1–5 | — | 0,21 / 0,22 / 0,21 | 2015 pendente |

**Efeito da harmonização na variação 2015→2019 (Brasil, total):**

| Indicador | Δ no painel (p.p.) | IC 95% do Δ | No painel | Harmonizado (p.p.) | Harmonizado |
|---|---|---|---|---|---|
| CAPACETE_AS_VEZES_OU_MAIS | −3,69 | [−6,46; −0,92] | confirmada | −2,6 a −2,7 | **acaso** |
| CONDUZIU_VEICULO | +1,69 | [−0,18; 3,56] | acaso | +1,95 | **confirmada** |
| CAPACETE_QUALQUER_USO | −3,53 | — | — | −2,3 a −2,5 | magnitude cai cerca de 1 p.p. |

Método: diferença das estimativas pontuais harmonizadas, com a meia-amplitude do IC atual (`nr_effect.py`). É aproximado; a confirmação virá do recálculo completo.

**2019–2024, 13 a 17 anos**
- **Alunos (7 indicadores):** CONDUTOR_CELULAR, BRIGA_LUTA_FISICA, AGREDIDO_PAIS, AGREDIDO_OUTROS, ACIDENTE_OU_AGRESSAO, TOQUE_SEM_CONSENTIMENTO, RELACAO_SEXUAL_FORCADA.
- **Escola (6 indicadores):** ESCOLA_LOCAL_ASSALTOS, ESCOLA_LOCAL_TIROS, ESCOLA_LOCAL_AGRESSAO, ESCOLA_LOCAL_ASSASSINATO, ESCOLA_LOCAL_VIOLENCIA_SEXUAL e ESCOLA_SUSPENDEU_AULAS.
- **Evidência comum:** mesma variável e redação idêntica; mesma convenção de não resposta; ambas as edições reproduzem as publicações.
- **Recomendação:** "comparável com ressalvas", **a confirmar pelo pesquisador** em `comparability_decisions.csv`.
- **Tema 17:** descrever como "% de escolares em escolas cujo diretor relatou…" (informante: escola).
- **ESCOLA_LOCAL_DROGAS:** não comparável, corretamente ("ou usando" acrescentado em 2024).

**Série oficial do 9º ano, capitais (2009–2019) + 2024 calculado** (10 tabelas, sem 10.3 e 10.12)
- 2009–2019 são **valores publicados** (estatística experimental).
- 2019 nos microdados: **REPRODUZ** os totais das capitais (Δ 0,00 p.p.) e é **PRÓXIMO** nos demais recortes (até 1,72 p.p.).
- 2024 está **calculado, não validado** (o IBGE não publicou), com a mesma convenção de 2019, que agora tem respaldo documental (p. 18).
- Recomendação: comparável com ressalvas, rotulado "2024 calculado (não oficial)" e "série experimental do IBGE".
- **10.3:** NÃO VALIDADO. Mantido fora.

**Tentativa 2009/2012/2015 A1:** NÃO VALIDADO / PENDENTE. A regra de abandono (§F) é a pista concreta para resolver a pendência M6.

## Correspondência painel × fontes (tarefa 7)

**Publicados:** rastreáveis até a célula. 30.016 valores, 0 sem origem, 0 divergências [R].
- Destes, 56 estão "em revisão" (tabela 8.1) e 120 são símbolos.
- O painel os mostra com o status, sem convertê-los.

**Calculados:** rastreáveis à regra (`indicators.toml`), à edição e ao arquivo; não há célula de origem, por natureza.

**Não devem ser apresentados como validados hoje:**
- todo ponto de 2015 da série de 13 a 17 anos;
- `CAPACETE_AS_VEZES_OU_MAIS` (nenhuma edição);
- os pontos 2024 da série do 9º ano (calculados, não validados);
- `NONO_CINTO_FRENTE_OU_TRAS`;
- qualquer selo "Mudança confirmada" envolvendo 2015.

## E. Plano de trabalho priorizado

**Bloqueadores** (antes de usar números da série no texto do TCC)

| # | Tarefa | Validação |
|---|---|---|
| B1 | Declarar numpy e pandas (`requirements.txt` e `pyproject.toml`); documentar a extração dos microdados, com manifesto de nomes, SHA-256 e a renomeação de 2009 | venv limpo → 121 aprovados + 1 pulado; `run_all` com código de saída 0 |
| B2 | **Harmonizar a não resposta na série** (ver F) | Critérios do §F |
| B3 | Regra de status baseada em evidência: edição sem validação → PENDING_REVIEW para o trecho que a inclui; série e "mudança confirmada" só com decisão registrada (ou rótulo explícito "proposta automática"); pesquisador preenche `comparability_decisions.csv` | Teste unitário + painel sem selo para trechos pendentes |
| B4 | Obter as **tabelas da PeNSE 2015 Amostra 2** (2.11.1–2.11.10; ftp.ibge.gov.br/pense/2015/) e validar estimativa, IC e escolha do estrato | Mesmos critérios de 2024 (≥ 95% REPRODUZ) |

**Importantes**
- **I1:** avisos no painel: "estatística experimental (IBGE, 2022)", "2024 calculado" e "teste entre anos oficiais aproximado".
- **I2:** limiar de CV em configuração única com fonte citada, ou declarado como critério de projeto com referência; tirar o 15 fixo do JS.
- **I3:** confirmar o informante pelos dicionários (B* = aluno, E* = escola) e reduzir os 26.700 casos "inferidos".
- **I4:** corrigir as contradições da tabela acima; registrar no ADR o `liv101955.pdf`.
- **I5:** um teste que recalcule (ou compare o hash de um recálculo) quando houver microdados; marcar os testes de "saídas gravadas".
- **I6:** script gerador para a tentativa 2009/2012/2015 A1 e novo teste com a regra de abandono.
- **I7:** comparador passa a conferir categorias de resposta.
- **I8:** pedir ao IBGE a regra de derivação da tabela SH 10.3.
- **I9:** decisões do pesquisador sobre P2, P3 e P6.

**Opcionais**
- **O1:** replicar o modelo logístico de tendência do IBGE (Tabelas 20 e 21) como validação extra.
- **O2:** limpar o ZIP (`.ruff_cache`) e os nomes com prefixo de hash.
- **O3:** corrigir o gerador do `docs/09`.
- **O4:** incluir `liv101955.pdf` em `data/reference` e no `docs/11`.
- **O5:** teste com leitor de tela e SUS.

**Documentação externa necessária:**
1. Tabelas da PeNSE 2015 Amostra 2 (estimativa e IC por indicador), para validar o ponto 2015 e o estrato.
2. Regra de derivação da SH 10.3 (plano tabular específico da análise histórica, citado na 4ª capa do `liv101955`).
3. Notas técnicas da publicação PeNSE 2024, seção de precisão, para o limiar de CV. Se não houver, assumir o critério como do projeto.
4. Publicação PeNSE 2009 (tabela 8.1) e convenções da publicação 2015 (símbolo "-").

## F. Primeira correção recomendada

**Harmonizar a convenção de não resposta na série de microdados**: "sem resposta" entra no denominador, "abandono de questionário" sai — a regra da série oficial do IBGE. Para 2015, o abandono é reconstruído a partir do código 99. B1 entra no mesmo pacote, porque sem ele os critérios não são verificáveis em ambiente limpo.

**Por que primeiro**
- É o único problema encontrado que **muda conclusões numéricas do TCC**.
- Tem fonte oficial: `liv101955.pdf`, p. 18, nota 7, e Quadro 2.
- Tem um teste objetivo e independente: reproduzir os valores oficiais de 2015 da série do 9º ano.
- Não depende de documento externo.

**O que muda**
- Em `editions.toml`, por edição: códigos de "sem resposta" e de "abandono".
- Para 2015, a regra de reconstrução: 99 numa pergunta sem nenhuma resposta efetiva em perguntas posteriores = abandono; caso contrário, sem resposta.
- A validação contra as tabelas publicadas de 2015 continua com a convenção daquela publicação (99 fora, Nota 03). Assim ficam separadas a "convenção de validação" e a "convenção da série".
- O texto fixo "< 0,2 p.p." é substituído pelo efeito medido por indicador.

**Critérios de aceitação** (todos objetivos)
1. **Teste A, reprodução da série do IBGE** (microdados 2015 A1, total das capitais):
   - Tabelas 10.1, 10.2, 10.4–10.8 e 10.11 com |Δ| ≤ 0,05 p.p. em relação a `Serie_9ano…xls` (2015).
   - Hoje, com "99 fora", as diferenças vão de 0,07 a 0,32 p.p.; no meu teste exploratório, o máximo foi 0,047.
   - Os recortes por capital não podem piorar em relação ao estado atual.
2. **Teste B, sem regressão:** `microdata_validation*.csv` de 2019 e 2024 ficam byte a byte iguais (a regra já é a delas).
3. **Teste C, unitário com dados sintéticos:** aluno com 99 seguido de respostas → entra no denominador; aluno com 99 até o fim → fica fora; 2019/2024 sem mudança.
4. **Relatório gerado** listando, por indicador, a variação 2015→2019 antes e depois e todo selo de significância que mudou. Esperado: ao menos `CAPACETE_AS_VEZES_OU_MAIS` e `CONDUZIU_VEICULO` no total Brasil.
5. **Ressalvas** com efeito medido; teste garantindo que não há mais texto fixo de magnitude.
6. **Suíte completa** passa em venv limpo criado só com os arquivos de dependência; duas execuções de `run_all` geram hashes idênticos.
7. **Documentação:** `docs/04` (ADR com citação de página), `docs/06`, `docs/10` e `docs/12` atualizados. Nenhuma estimativa oficial é alterada.

Se o Teste A falhar (|Δ| > 0,05 p.p.), a correção não é aplicada à série: o ponto de 2015 fica PENDENTE e registra-se o resultado.

---

## Adendo (27/10, 08:19) — tabelas da PeNSE 2015 Amostra 2 recebidas

Arquivos novos: `Amostra_2_Tema_11_Seguranca.xls` (15 tabelas, 2.11.1–2.11.15) e `Amostra_2_Tema_01_Informacoes_Gerais.xls` (10 tabelas, 2.1.1–2.1.10). Isso resolve a pendência **B4 / M3**.

Procedimento: `scripts/valida_2015_a2.py`, um leitor de conferência independente da pipeline. Ele compara os microdados com as tabelas 2.11.1–2.11.7, 2.11.9 e 2.11.10 na convenção da publicação de 2015 (código 99 fora do denominador). Resultado completo, recorte a recorte: `validacao_2015_a2.csv`.

| Verificação | Resultado |
|---|---|
| Estimativas (900 recortes = 10 indicadores × 3 faixas etárias × 6 territórios × 5 recortes) | **100% REPRODUZ**, Δ máx 0,0000 p.p. [R] |
| IC com o estrato atual (`ESTRATOGEOREG`, só 5 estratos = as regiões) | Só 64,6% dos recortes com limites ≤ 0,15 p.p.; erro máximo de 5,67 p.p. [R] |
| IC com `ESTRATO_EXP` (56 estratos; o mesmo do Quadro 2 da publicação de 2022) | **100%** com limites ≤ 0,15 p.p.; mediana 0,012, máx 0,079 [R] |

**Consequências** (substituem os itens correspondentes acima):

- **R3 (ponto de 2015 sem validação):** resolvido nas estimativas. As 10 séries passam a ter evidência nas três edições. `CAPACETE_AS_VEZES_OU_MAIS` está validado em 2015 (a definição publicada em 2015); a outra definição, `CAPACETE_QUALQUER_USO`, está validada em 2019 e 2024. As duas usam a mesma variável e o mesmo desenho, ambos validados.
- **R10 (estrato de 2015):** passa de "divergência documental" a **erro confirmado**, com severidade de **bloqueador**. A configuração usa o estrato da Nota 01/2018 (Quadro 3), mas as tabelas publicadas só são reproduzidas com `ESTRATO_EXP`.
  - Impacto medido nos selos 2015→2019 do painel: corrigir só o estrato muda **6 de 420** selos. São eles: arma branca/NE/privada e arma de fogo/NE/mulheres passam a acaso; cinto frente/Sul, conduziu veículo/NE/privada, conduziu veículo/N/13–15 e escola insegura/CO passam a confirmada.
  - A Amostra 1 provavelmente tem o mesmo problema (Quadro 2 da publicação de 2022). Ela hoje só entra na tentativa 2009/2012/2015 A1.
- **R2 (não resposta)** continua válido. A publicação de 2015 exclui o 99 (confirmado agora pela reprodução exata), e 2019/2024 incluem o "sem resposta". A série harmonizada ainda precisa da correção do §F.
- **Pipeline:** as 25 abas novas são inventariadas, mas **nenhum adaptador as reconhece**.
  - O melhor candidato é `PENSE_2024_IC`, com pontuação 0,6, abaixo do mínimo de 0,7. A pipeline gera alertas `ADP000` (revisão) em vez de ler errado, comportamento correto.
  - O leitor de títulos não reconhece "escolares com idade de 13 a 17 anos" e marca a população como PENDENTE.
  - Por isso a validação de 2015 ainda não entra em `microdata_validation_summary.csv`.

### Sequência revisada

1. **Correção 1 — erros de configuração confirmados (pequena, sem decisão metodológica em aberto):**
   - B1: declarar numpy e pandas.
   - Trocar o estrato de 2015 A2 (e verificar o da A1) para `ESTRATO_EXP`, com a evidência registrada em `editions.toml` e no `docs/04`.
   - Adaptador `PENSE_2015_A2`, mais o reconhecimento de "escolares com idade de 13 a 17 anos" no leitor de títulos, para que a validação de 2015 rode dentro da pipeline.

   **Critérios de aceitação:**
   - `microdata_validation_summary.csv` passa a ter linhas `PENSE_2015_A2` com estimativas 100% REPRODUZ e limites do IC ≤ 0,15 p.p. em ≥ 95% dos recortes. O resultado de referência é o deste adendo: 100%.
   - As validações de 2019 e 2024 ficam byte a byte iguais.
   - As 25 abas da Amostra 2 são lidas sem `ADP000` nas tabelas de layout padrão. A 2.1.8 (73 colunas) e a 2.11.14 podem exigir tratamento próprio e, se ficarem de fora, aparecem no `unparsed_report`.
   - Um relatório lista os selos de significância que mudaram (referência: 6 de 420).
   - Todos os testes passam numa instalação limpa.
2. **Correção 2 — harmonização da não resposta na série (antigo §F),** com os mesmos critérios. Agora há validação de 2015 nas duas convenções: a da publicação (99 fora), para validar, e a do IBGE para a série (sem resposta entra, abandono sai).
3. **B3 — status baseado em evidência e decisões do pesquisador.** Agora as três edições têm validação: a decisão passa a ser sobre o conceito, não sobre a falta de dados.

### Checagem extra dos pesos (Tema 01 de 2024 e Tabela 2.1.1 de 2015 A2, recebidos às 08:22)

| Total de escolares de 13 a 17 anos, Brasil | Microdados (soma dos pesos) | Publicado | Situação |
|---|---|---|---|
| 2015 Amostra 2 (`PESO`) | 13.199.861,8 | 13.199.861,8 (2.1.1) | REPRODUZ exatamente |
| 2024 (`PESO_ALUNO_FREQ`) | 12.359.432,9 | 12.359.708,8 (1.1.1) | PRÓXIMO: Δ 276 escolares (0,002%), causa não identificada; não afeta percentuais na 4ª casa |

O `Guia_Tabelas_PeNSE_2024_20260525_1.xlsx` é idêntico (MD5) ao guia já presente em `data/reference/`.
