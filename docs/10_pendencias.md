# Pendências e limites conhecidos

## Exigem revisão humana (decisão do pesquisador)

| # | Pendência | Onde aparece | Como resolver |
|---|---|---|---|
| P1 | Texto das perguntas de origem | `question_text` | **Resolvido em grande parte:** preenchido pelos dicionários de microdados do IBGE para 2009 e 2015 A1 (mapeamento manual em `config/question_map.csv`, conferir) e para as tabelas de 2019, 2024 e da série 9º ano cuja ligação foi comprovada por reprodução numérica. Pendente só para tabelas sem indicador calculado (ex.: 9.13–9.15, 9.18, 9.20, 9.22, 9.23, 17.3) |
| P2 | Tabela 8.1 (2009): a que indicador se referem as colunas por dependência administrativa | 56 observações `REVIEW_REQUIRED` (`VAL022`/`HDR006`) | Conferir a publicação PeNSE 2009; registrar a interpretação no adaptador |
| P3 | Denominador das distribuições condicionais (17.2 "por número de vezes") | `denominator_status = REGRA_DERIVADA_REVISAR` (312 observações aprovadas) | Confirmar na nota técnica que o denominador é o grupo da coluna "Total" |
| P4 | Informante "escolar" inferido pela ausência de menção à escola no título | `informant_method` | Confirmar no questionário do aluno |
| P5 | Limiares de CV (30% "baixa precisão"; 15% "boa" × "razoável" no painel) | `settings.toml`, `app.js` | **Não resolvido.** Nenhum documento recebido define o limiar (o manual de 2019 só dimensiona a amostra para CV de 4% em P = 50%). Conferir as notas técnicas da PeNSE 2024; sem fonte, declarar como critério de projeto |
| P6 | Significado do símbolo "-" na tabela de 2015 Amostra 1 (zero absoluto × não aplicável) | 120 células `NOT_AVAILABLE` (**não resolvido**) | Conferir as convenções da publicação 2015 antes de qualquer conversão |
| P7 | Códigos IBGE dos municípios das capitais | `territories.csv` (`code_source`) | Conferir com a DTB do IBGE |
| P8 | Comparabilidade 2009/2015 A1 × 2024 entre **tabelas publicadas** | 16 pares `NOT_COMPARABLE` (população) | Mantido: universos diferentes. A comparação ao longo do tempo é feita pelos microdados (13 a 17 anos: 2015 A2, 2019, 2024; 9º ano: 2015 A1, 2019, 2024) |

## Microdados (série harmonizada) — situação em 27/10/2026

| # | Pendência | Situação | Evidência / próximo passo |
|---|---|---|---|
| M1 | Confirmar a comparabilidade proposta | **Em grande parte concluída (27/10/2026, D29).** Decisões registradas: 32 de 36 (`COMPARABLE_WITH_CAVEATS`), com 11 exclusões de edição (TRAJETO_INSEGURO e ESCOLA_INSEGURA: 2015 fora · 9 indicadores do 9º ano: 2024 fora). Sem decisão: ESCOLA_LOCAL_DROGAS (proposta automática NOT_COMPARABLE, não marcada pelo pesquisador) e 3 pendentes (NONO_BRIGA_LUTA_FISICA, NONO_CINTO_FRENTE_OU_TRAS, CAPACETE_AS_VEZES_OU_MAIS). Matriz: `reports/matriz_comparabilidade_2026-10-27/` | Decidir ESCOLA_LOCAL_DROGAS; validar o 9º ano de 2024; resolver 10.3 |
| M2 | Regra de não resposta de 2019 | Resolvida | Dicionário 2019: 9 = Sem resposta, −2 = Abandono; totais reproduzidos |
| M3 | Validar 2015 Amostra 2 contra tabelas publicadas | **Resolvida** | Tabelas 2.11.1–2.11.10 recebidas: 10/10 indicadores VALIDADO, estimativa e IC em todos os recortes (estrato `ESTRATO_EXP`, D22) |
| M4 | Venda de drogas (E01P81 × E01P81A) | Resolvida | 2024 acrescenta "ou usando" → não comparável |
| M5 | Regra da tabela oficial 10.3 (cinto, frente ou trás, 9º ano) | **Não resolvida** | Definição do glossário do IBGE testada em 10 variantes; não reproduz 2015 (Δ 0,62) nem 2019 (Δ 0,80). Fora da série. Pedir ao IBGE o código de derivação / plano tabular da análise histórica |
| M6 | Regra harmonizada de 2009/2012/2015 A1 na série do 9º ano | **2015 A1 resolvida; 2009 e 2012 abertas** | 2015 A1 reproduz a série oficial com a regra de abandono (D21). 2009 e 2012 não têm código de não resposta nos dicionários; a série usa os valores oficiais publicados |
| M7 | Convenção de não resposta misturada na série | **Resolvida** | D21: série harmonizada; efeito medido em `microdata_nonresponse_effect.csv` |
| M8 | Estrato de 2015 | **Resolvida** | D22: A2 `ESTRATO_EXP`, A1 `ESTRATOGEOREG` (decidido pela reprodução dos IC) |
| M9 | `CAPACETE_AS_VEZES_OU_MAIS` | Fora da série (`series_exclude`) | Só 2015 publicou essa definição; voltar só com validação das três edições e decisão |
| M10 | `CAPACETE_QUALQUER_USO` em 2015 | Ponto fora da série (evidência AUSENTE) | 2015 publicou a outra definição; série usa só 2019–2024 |
| M11 | Diferença de 276 escolares entre a soma dos pesos de 2024 (13 a 17 anos) e a tabela 1.1.1 | Aberta, sem efeito nos percentuais | Causa não identificada |

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
| Comparabilidade (tabelas) | ✔ só conclui "não comparável" ou "pendente" | aprovar pares com justificativa |
| Comparabilidade (microdados) | ✔ só PROPÕE (proposta automática, nunca decisão) | registrar decisão completa em `comparability_decisions.csv` |
| Série histórica | ✔ só edições com evidência; selo "Diferença significativa a 5%" só com decisão | decidir |
