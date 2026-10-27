# Estado do projeto — 27/10/2026 (após a auditoria e as correções)

Execução real: `python scripts/run_all.py` em 27/10/2026 (Python 3.13.17), em dois ambientes:
a pasta de trabalho e uma cópia limpa, com venv criado **só** com `requirements.txt` e
microdados extraídos dos ZIPs originais por `scripts/extract_microdata.py`. Evidências em
`reports/auditoria_2026-10-27/`.

## Números da execução

| Medida | Valor |
|---|---|
| Arquivos inventariados / únicos / duplicados | 45 / 40 / 2 |
| Abas lidas (por família) | 278 (2015 A1 4 · **2015 A2 15** · série 9º ano 12 · 2019 78 · 2024 IC 78 · 2024 CV 78 · 2009 13) |
| Estimativas publicadas extraídas / aprovadas | 33.220 / 31.316 (VALID 32.140; com ressalva 904; em revisão 56; símbolo 120) |
| Itens não interpretados | 0 |
| Estimativas calculadas dos microdados | 35.084 (2015 A1, 2015 A2, 2019, 2024; 2015 em duas convenções de não resposta) |
| Validação contra tabelas publicadas | 2015 A2: 10/10 VALIDADO · 2015 A1 (série 9º ano): 9 validados, 10.3 não · 2019: 34 validados, 10.3 não · 2024: 24/24 |
| Comparabilidade (microdados) | 33 propostas COMPARABLE_WITH_CAVEATS, 2 PENDING_REVIEW, 1 NOT_COMPARABLE — **todas propostas automáticas; 0 decisões registradas** |
| Pontos da série | 28.865 (3.585 diferenças significativas aguardando decisão; 0 "mudança confirmada") |
| Testes | pasta de trabalho: **150 aprovados, 0 falhas, 0 pulados** · venv limpo: **140 aprovados, 0 falhas, 1 pulado** (painel: playwright é opcional) |
| Reprodutibilidade | 2 execuções no venv limpo: 43 de 46 saídas idênticas byte a byte; as 3 diferentes só têm carimbo de data/hora (`run_manifest.json`, `docs/09`, `relatorio_qualidade.md`). As mesmas 43 são idênticas às da pasta de trabalho (numpy/pandas de versões diferentes) |

## O que mudou (D21–D24 em `docs/04`)

1. **2015 Amostra 2:** tabelas 2.11.1–2.11.15 lidas pelo adaptador novo `PENSE_2015_A2`; a
   validação dos microdados reproduz estimativa e IC de todas as tabelas usadas (2.11.1–2.11.7,
   2.11.9, 2.11.10).
2. **Estrato de 2015:** A2 `ESTRATO_EXP` (IC 100% reproduzidos × 64,6% com `ESTRATOGEOREG`);
   A1 `ESTRATOGEOREG` (97,1% × 64,8%). Decidido pela reprodução, não pelo documento.
3. **Não resposta:** convenção da publicação (validação) × convenção da série (sem resposta
   entra, abandono sai; IBGE 2022, p. 18, nota 7). Em 2015 o abandono é reconstruído. A Amostra 1
   reproduz a série oficial de 2015 (9 tabelas, total das capitais, |Δ| ≤ 0,047 p.p.).
4. **Governança da série:** proposta automática ≠ decisão; edições sem evidência fora da série;
   "mudança confirmada" só com decisão completa registrada; `CAPACETE_AS_VEZES_OU_MAIS` fora.
5. **Reprodutibilidade:** numpy e pandas declarados; manifesto `config/microdata/source_files.csv`
   com SHA-256; `scripts/extract_microdata.py` (trata o nome com espaço de 2009); testes que
   recalculam a partir dos microdados.
6. **Matriz de evidências** gerada: `docs/13_matriz_evidencias.md` e
   `data/curated/methodological_evidence_matrix.csv`.

## Pendências que continuam abertas (não declaradas resolvidas)

* **Decisões de comparabilidade (M1):** cabe ao pesquisador registrar.
* **Tabela 8.1 de 2009 (P2), símbolo "–" de 2015 (P6), regra da tabela 10.3 (M5), limiares de CV
  (P5):** sem evidência documental suficiente.
* **2009 e 2012 pelos microdados (M6):** sem código de não resposta nos dicionários; série usa os
  valores oficiais publicados.
* **Diferença de 276 escolares** entre a soma dos pesos de 2024 e a tabela 1.1.1 (M11).
