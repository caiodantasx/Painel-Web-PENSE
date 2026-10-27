# Guia: interpretar e construir a série histórica

## Atualização (27/10/2026): série harmonizada pelos microdados

Com os microdados de 2015 (Amostras 1 e 2), 2019 e 2024 o mesmo indicador (mesma variável,
mesmos códigos, mesmo universo) é recalculado em cada edição com o desenho amostral e
conferido contra as tabelas do IBGE (2015 A2: Tema 11; 2019: Temas 9, 17 e série do 9º ano;
2024: Temas 9 e 17). Detalhes em `12_microdados.md`; evidências em `13_matriz_evidencias.md`.

Regras da série (D21–D23 em `04_decisoes_metodologicas.md`):

1. **Não resposta harmonizada:** "sem resposta" no denominador, "abandono" fora, em todas as
   edições. Em 2015 o valor da série difere do publicado pelo efeito medido (até 1,2 p.p.);
   o painel mostra os dois.
2. **Só edições com evidência:** uma edição sem tabela publicada que reproduza o cálculo fica
   fora da série (o ponto continua na base, marcado "fora da série").
3. **Proposta ≠ decisão:** a pipeline só propõe. Para aprovar, copie a linha de
   `config/microdata/comparability_decisions_MODELO.csv` para
   `config/microdata/comparability_decisions.csv` e preencha **todos** os campos:

   ```csv
   indicator_key,final_status,justification,evidence_reference,reviewer,decision_date
   <INDICADOR>,COMPARABLE_WITH_CAVEATS,"<justificativa: evidências e limitações>","<documentos e páginas consultados>",<nome do responsável>,<AAAA-MM-DD do dia do registro>
   ```
3b. **Excluir uma edição da série principal** (sem excluir o indicador): uma linha completa em
   `config/microdata/series_exclusions.csv` — `indicator_key,edition_id,reason,evidence_reference,reviewer,decision_date`.
   Sem linha, nada é excluído; linha incompleta, edição inexistente ou que o indicador não tem,
   data inválida ou futura, ou linha duplicada interrompe a pipeline (D26). Texto em justificativas
   nunca exclui edição: só este arquivo.
4. **"Diferença significativa a 5%"** só aparece com decisão registrada, evidência nas duas edições e
   IC 95% da diferença sem o zero. Sem decisão: "diferença significativa · aguardando decisão".
   Significativa não quer dizer grande, importante ou explicada (D27).
5. Série oficial do 9º ano (IBGE 2009–2019) é **estatística experimental**; o teste entre anos
   publicados é aproximado e nunca recebe o selo "Diferença significativa a 5%"; 2024 é calculado (não oficial).

## Situação das tabelas publicadas

Os 16 pares candidatos avaliados (2009 × 2024 e 2015 × 2024) são `NOT_COMPARABLE`. A
causa comum é o **universo**: 2009 e 2015 medem escolares do **9º ano**; 2024, escolares
de **13 a 17 anos**. Alguns pares têm ainda período diferente (8.6 × 9.16: 30 dias ×
12 meses) ou pergunta diferente (1.6.1 "área de risco" × 17.1 "presenciou ou ouviu
falar").

Por isso o painel **não** exibe série ligando as edições e explica o motivo na página
"Série histórica". Isto é um resultado do TCC, não uma falha: mostra que nomes parecidos
não garantem a mesma medida.

## Como uma série pode ser aprovada

1. **Mesma população:** obter tabelas com o mesmo universo. Exemplos a buscar no IBGE:
   recortes de 2024 restritos ao 9º ano, ou tabelas de 2015 Amostra 2 (13 a 17 anos),
   se publicadas para os mesmos indicadores.
2. **Mesmo período de referência** e mesma unidade.
3. **Mesma pergunta e categorias** — conferir no questionário de cada edição.
4. **Mesmo informante** (escola × escolar).
5. **Notas metodológicas** sem mudanças que alterem o indicador.

Com isso, registre em `config/comparability_decisions.csv`:

```csv
concept_id,left_indicator_id,left_category,right_indicator_id,right_category,final_status,justification,evidence_reference,reviewer,decision_date
SUSPENSAO_AULAS_VIOLENCIA,PENSE_20XX__…,,PENSE_2024__17.2,,COMPARABLE_WITH_CAVEATS,"Mesma pergunta do questionário da escola (Q…); mesmo universo; mudança na amostra de escolas.",Nota técnica PeNSE 2024 p. X,Seu Nome,2026-11-10
```

Sem justificativa a decisão é ignorada. `COMPARABLE_WITH_CAVEATS` exige que a ressalva
esteja escrita na justificativa — ela aparece no painel.

## O que a série calcula (e o que não calcula)

| Calcula | Não calcula |
|---|---|
| uma observação por ano × série × território × recorte | estimativa combinada entre anos |
| estimativa e IC publicados de cada ano | teste de significância da diferença |
| variação absoluta (p.p.) e relativa (%) entre pontos consecutivos | tendência (regressão) |
| edições sem ponto para aquele recorte | média aritmética, salvo se `allow_descriptive_mean = true` |

Se a média for habilitada, ela sai rotulada como "estatística descritiva — não é
estimativa combinada nem evidência de tendência".

## Como ler uma variação

Duas estimativas cujos IC se sobrepõem **não** provam igualdade, e IC disjuntos não
substituem um teste com a variância da diferença (que depende do desenho amostral). Use a
variação como descrição e cite os IC de cada ano.
