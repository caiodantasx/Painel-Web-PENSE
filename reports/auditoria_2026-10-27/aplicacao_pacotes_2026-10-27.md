# Aplicação dos pacotes 1, 2 e 3 e registro da decisão de TRAJETO_INSEGURO (27/10/2026)

Projeto atualizado: `/home/claude/pense_tcc`. Cópia de segurança anterior à aplicação, verificada
(os 216 arquivos extraídos conferem com o hash): `/home/claude/backup_pense_tcc_2026-10-27_pre_pacotes/`
(`pense_tcc_pre_pacotes.tar.gz` + `.sha256`, `hashes_antes.txt`, `hashes_depois.txt`).

## O que foi aplicado (nesta ordem, `patch -p1`, sem rejeições)
1. **Pacote 1 — exclusão de edição da série principal (D26):** `config/microdata/series_exclusions.csv`
   (`indicator_key,edition_id,reason,evidence_reference,reviewer,decision_date`); linha inválida, incompleta,
   duplicada, com data inválida ou futura, ou cabeçalho fora do esquema interrompe a pipeline
   (`SeriesExclusionError`); a edição sai só da série principal; motivo no painel, em
   `microdata_comparability.csv` (`excluded_edition_ids`, `excluded_editions`), na matriz de evidências e em `docs/12`.
2. **Pacote 2 — rótulo (D27), versão preparada sobre o pacote 1:** estado `SIGNIFICATIVA_5PCT_COM_DECISAO`,
   selo "Diferença significativa a 5%"; critério estatístico inalterado; "aguarda decisão",
   "pode ser acaso" e "teste aproximado" preservados.
3. **Pacote 3 — correções (D28 e rastreabilidade):**
   * painel: "mudança provável: de 0,0 a 1,7 p.p." → "IC 95% da diferença: de +0,05 a +1,70 p.p. · o intervalo
     não inclui o zero" (casas decimais suficientes para preservar o sinal; frase vinda do mesmo indicador de
     significância do selo; só apresentação);
   * glossário: significância não é certeza absoluta, nem probabilidade de a mudança ser real, nem relevância ou causa;
   * evidências citadas nas decisões agora estão no projeto, reproduzíveis na raiz:
     `reports/auditoria_2026-10-27/sensibilidade_6ano_trajeto.md` (+ `scripts/sensibilidade_6ano_trajeto.py`) e
     `reports/auditoria_2026-10-27/ic_diferenca_trajeto_2019_2024.md` (+ `scripts/ic_diferenca_trajeto.py`);
   * testes que supunham "nenhuma decisão registrada" passaram a montar a própria configuração temporária.

## Decisões registradas
| Arquivo | Registro | Responsável | Data |
|---|---|---|---|
| `config/microdata/series_exclusions.csv` | TRAJETO_INSEGURO × PENSE_2015_A2 fora da série principal (provisório; cobertura do 6º ano; sensibilidade é o motivo, não prova de erro) | Caio Justino De Andrade | 2026-10-27 |
| `config/microdata/comparability_decisions.csv` | TRAJETO_INSEGURO, 2019–2024: `COMPARABLE_WITH_CAVEATS` | Caio Justino De Andrade | 2026-10-27 |

Nome informado pelo pesquisador na conversa (27/10/2026, 13:30); data = dia do registro.

## Resultado (antes × depois)
* Mudou apenas TRAJETO_INSEGURO: série 2019–2024 (896 → 854 pontos), nenhuma comparação a partir de 2015,
  66 pontos 2019→2024 com o selo novo (antes "aguarda decisão").
* Idênticos: `microdata_estimates.csv`, `microdata_validation*.csv`, `microdata_nonresponse_effect.csv`,
  `pense_observations_approved.csv`; séries, comparabilidade e matriz dos outros 35 indicadores.
* 2015 preservado e consultável: publicado 13,10%, harmonizado 12,99% (Brasil, total).
* `data/raw`, `data/microdata`, `data/reference`, `config/reference`: 0 arquivos alterados.

## Testes (Python 3.13.17)
| Ambiente | Aprovados | Falhas | Pulados / não executados |
|---|---|---|---|
| sistema (pandas 3.0.5, numpy 2.5.3, playwright 1.63.0, Node 22) | 224 / 224 | 0 | 0 |
| venv só com `requirements.txt` (pandas 3.1.0, numpy 2.5.4) | 210 / 213 | 0 | 3 (painel: módulo e2e com 12 testes + 2 testes de navegador; playwright opcional) |

Por grupo (sistema): pacote 1 = 31; pacote 2 = 19; correções = 14; navegador = 12; regressão
(adaptadores, correções de 27/10, microdados, integração, harmonização) = 53; todos aprovados.
Pipeline `python scripts/run_all.py`: código 0, 276 s, sem erro.

## Reproduzir
```bash
pip install -r requirements.txt            # opcional: playwright + "playwright install chromium"
python scripts/extract_microdata.py        # se data/microdata/ estiver vazio
python scripts/run_all.py                  # pipeline completa + testes + painel
python -m pytest -q                        # suíte
python reports/auditoria_2026-10-27/scripts/sensibilidade_6ano_trajeto.py
python reports/auditoria_2026-10-27/scripts/ic_diferenca_trajeto.py
```

## Limitações que continuam abertas
1. Regra de não resposta de 2019 e 2024 sustentada só pela reprodução das tabelas (lacuna documental).
2. Inclusão de técnico integrado e normal/magistério em 2024: não confirmada.
3. Número da questão em 2019 e 2024: pendente.
4. Recorte do 6º ano pelo ano autodeclarado (aproximação da cobertura por turma).
5. 2019→2024 significativa por margem pequena (|d|/EP ≈ 2,07; limite inferior 0,03 a 0,06): conclusão frágil.
6. Teste por aproximação normal (z = 1,96), sem método oficial publicado para esta comparação.
7. `comparability_decisions.csv` não valida formato nem data futura (o de exclusões valida); sugestão para um próximo pacote.
8. Os outros 35 indicadores seguem sem decisão; pendências anteriores (10.3, limiares de CV, 8.1, "–" de 2015, 2009/2012).
