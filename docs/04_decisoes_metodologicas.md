# Registro de decisões metodológicas e técnicas

Cada decisão: contexto, decisão, alternativa rejeitada e consequência.

### D01 — Reconstruir a pipeline como pacote modular
**Contexto:** script único sem adaptadores e com saídas analíticas vazias.
**Decisão:** pacote `src/pense` com etapas independentes e testáveis.
**Rejeitado:** remendar o script (não permitiria testes por componente).

### D02 — Cabeçalho a partir de células mescladas, nunca por posição
**Contexto:** a mesma informação muda de coluna entre tabelas (ex.: 9.2 tem 31 colunas;
17.2 tem 10).
**Decisão:** o caminho de rótulos de cada coluna vem das mesclagens nativas; o papel
(estimativa/IC/CV) vem do rótulo final.
**Consequência:** sem mesclagens (CSV), o caminho é inferido e marcado `HDR005`.

### D03 — Um motor comum, adaptadores como famílias
**Decisão:** as famílias diferem em detecção, códigos e metadados de edição; a leitura de
cabeçalho/stub é compartilhada. Evita código duplicado e torna novas famílias baratas.

### D04 — Escolha da família por evidência pontuada
**Decisão:** limiar 0,7 e margem 0,1; a evidência fica no inventário. Ambiguidade →
`ADP000` (revisão), nunca escolha silenciosa.

### D05 — Símbolos não viram números
**Decisão:** `-`, `..`, `...`, `x` ficam como símbolo e estimativa nula
(`NOT_AVAILABLE`). Converter `-` em zero exige decisão registrada.

### D06 — Valores publicados nunca são arredondados ou corrigidos
**Decisão:** precisão original preservada; artefatos (`100.00000000000016`) e IC negativo
publicado (2009) geram alerta, não correção. O painel arredonda só na exibição.

### D07 — CV vem da aba (CV) e é conferido
**Decisão:** abas CV não geram observações próprias; anexam o CV e conferem a estimativa
(`VAL010`). Erro-padrão é **derivado** do IC simétrico e rotulado como tal
(`standard_error_method`), nunca apresentado como publicado.

### D08 — Recorte publicado em mais de uma tabela
**Contexto:** Brasil e regiões aparecem em `x.y.1` e `x.y.2`.
**Decisão:** a primeira ocorrência (ordem de tabela) é canônica; as demais recebem
`analytical_duplicate_of` e são conferidas (`VAL020`). A camada aprovada só tem canônicas.

### D09 — "13 a 17 anos" como seção = Total
**Decisão:** quando o grupo de idade da seção coincide com o universo do título, ele é o
total (`age_group = Total`), com o rótulo original preservado em `row_group_label`.

### D10 — Rótulos de sexo harmonizados, originais preservados
**Decisão:** Masculino/Feminino (2009) → Homem/Mulher (2024) para filtro único;
`dimension_labels_original` guarda o rótulo publicado. A mudança de rótulo é registrada
como diferença contextual na comparabilidade.

### D11 — Comparabilidade nunca é automática no sentido positivo
**Decisão:** a regra automática só conclui `NOT_COMPARABLE` (diferença essencial:
população, período, informante, unidade, tipo de estimativa) ou `PENDING_REVIEW`.
`COMPARABLE` exige linha em `comparability_decisions.csv` com justificativa; sem
justificativa a decisão é ignorada. Semelhança de título é só evidência auxiliar.
**Atualização (27/10/2026):** a série dos microdados segue a mesma regra — ver D23.

### D12 — Período normalizado em código
**Decisão:** "últimos 30 dias" e "30 dias anteriores à pesquisa" → `30_DIAS`; a redação
diferente é registrada como diferença contextual, não essencial.

### D13 — Validação sinaliza, não exclui
**Decisão:** severidades ERROR (bloqueia), REVIEW (decisão humana), WARNING (aprovável
com ressalva), INFO (rastreabilidade); classes: erro confirmado, possível anomalia,
possível valor extremo legítimo, não validado, informativo.

### D14 — Soma de distribuições com nota de não-resposta
**Decisão:** soma < 100% em tabela cuja nota informa que não-respostas não são
apresentadas vira INFO (explicado). Sem nota, WARNING. Múltipla resposta: regra não se
aplica. Nada é redistribuído.

### D15 — Limite de CV
**Decisão:** CV ≥ 30% → WARNING "baixa precisão" (limiar configurável em
`settings.toml`). **Pendente:** confirmar o limiar na nota técnica da PeNSE 2024. O painel
também usa 15% para separar precisão "boa" de "razoável": **critério de projeto sem fonte
oficial** (continua pendente; não declarar resolvido).

### D16 — Valores incomuns por mediana/MAD, só para percentuais
**Decisão:** z robusto > 3,5 entre UFs (ou capitais) do mesmo recorte → INFO. Contagens
ficam de fora (refletem tamanho da população).

### D17 — Sem testes de significância
**Decisão:** o sistema exibe IC publicados e variações descritivas; não declara diferença
significativa (falta informação do desenho amostral para variância de diferenças).
**Atualização:** vale para as tabelas publicadas. Para os microdados, a diferença entre anos
usa o erro-padrão de desenho (amostras independentes); mesmo assim ela só recebe o selo
"Diferença significativa a 5%" com decisão registrada (D23, D27). Na série oficial do 9º ano o
teste entre anos publicados é aproximado (EP derivado do IC) e nunca recebe o selo.

### D18 — CSV/JSON em vez de Parquet
**Decisão:** volume pequeno; CSV abre em qualquer ferramenta; evita `pyarrow`.

### D19 — Mapa só para percentuais por UF
**Decisão:** coroplético de contagens absolutas é desativado; capitais não são pintadas no
polígono da UF (enganaria a leitura).

### D20 — Malha das UFs
**Decisão:** dissolução da malha municipal do IBGE publicada em `tbrugz/geodata-br` (CC0),
simplificada para uso visual (`scripts/build_uf_geometry.py`). A API de malhas do IBGE não
era acessível no ambiente de desenvolvimento; trocar pela malha oficial mais recente é
uma pendência simples (mesmo script).

## Decisões de 27/10/2026 (auditoria independente)

### D21 — Duas convenções de não resposta: publicação × série
**Contexto:** 2015 publicou os indicadores com o código 99 ("não informado") fora do
denominador (Nota metodológica n. 03); 2019 e 2024 publicaram com "sem resposta" (9 / −9)
dentro e "abandono" (−2) fora. A série misturava as duas regras; o efeito chega a 1,2 p.p.
(capacete) e inverte conclusões.
**Fonte:** IBGE, *PeNSE — Análise de indicadores comparáveis dos escolares do 9º ano,
Capitais 2009/2019* (Estudos e Pesquisas n. 46, 2022), p. 18, nota 7: a série harmonizada
diferencia "quesito sem resposta" de "abandono de questionário"
(`data/reference/liv101955_PeNSE_indicadores_comparaveis_9ano_2009_2019.pdf`).
**Decisão:** cada estimativa traz `nonresponse_convention`. PUBLICAÇÃO valida contra as
tabelas da edição; SÉRIE (sem resposta entra, abandono sai) alimenta a série. Em 2015 o
abandono é reconstruído: 99 numa pergunta sem nenhuma resposta efetiva posterior (−1 = pulo
não conta como resposta). Tabelas da série comparável (referência com `@`) são validadas na
convenção da série.
**Evidência:** com a regra, a Amostra 1 reproduz os valores oficiais de 2015 da série do 9º
ano no total das capitais (9 tabelas, |Δ| ≤ 0,05 p.p.; antes, 0,07–0,32 p.p.); 2019 e 2024
ficam byte a byte iguais. Efeito por indicador: `data/curated/microdata_nonresponse_effect.csv`.

### D22 — Estrato de 2015 decidido pela reprodução dos IC publicados
**Contexto:** a Nota n. 01/2018 (Quadro 3) indica `ESTRATOGEOREG` para 2015; a publicação
de 2022 (Quadro 2) indica `ESTRATO_EXP` para a Amostra 1. Os documentos divergem.
**Decisão e evidência:**
* Amostra 2 → `ESTRATO_EXP`: reproduz os IC das tabelas 2.11.1–2.11.10 em 100% dos recortes
  (≤ 0,15 p.p.); `ESTRATOGEOREG` (5 estratos = regiões) só em 64,6% (erro máx. 5,7 p.p.).
* Amostra 1 → `ESTRATOGEOREG`: reproduz os IC da série oficial 10.x de 2015 em 97,1% de
  1.260 recortes; `ESTRATO_EXP` só em 64,8%.
Não se escolhe pelo documento mais recente nem pelo nome: decide a reprodução do publicado.

### D23 — Proposta automática ≠ decisão; série só com evidência
**Decisão:**
* Evidência por indicador × edição: DIRETA (reproduz tabela publicada), INDIRETA (declarada
  em `indirect_validation`: mesma variável e denominador reproduzem tabelas da edição — usada
  só na extensão 2024 do 9º ano, sem tabela oficial), FALHOU, AUSENTE.
* Edições AUSENTES ou FALHAS ficam fora da série (pontos preservados em
  `microdata_estimates.csv`). FALHOU em qualquer edição → `PENDING_REVIEW`.
* `series_exclude` retira indicadores por decisão metodológica (`CAPACETE_AS_VEZES_OU_MAIS`:
  só 2015 publicou essa definição).
* `proposed_status` é sempre proposta; `decision_status` = `PROPOSTA_AUTOMATICA` até existir
  decisão COMPLETA (status, justificativa, evidência, responsável, data) em
  `config/microdata/comparability_decisions.csv`. Decisão incompleta é ignorada e registrada
  no log. Modelo para preencher: `comparability_decisions_MODELO.csv` (não é lido como decisão).
* `change_status` da diferença entre anos: `SIGNIFICATIVA_5PCT_COM_DECISAO` (decisão + evidência +
  significativa; até D27 chamava-se `MUDANCA_CONFIRMADA`), `SIGNIFICATIVA_SEM_DECISAO`,
  `NAO_SIGNIFICATIVA`; na série oficial entre anos publicados, `SIGNIFICATIVA_APROXIMADA`.

### D27 — Rótulo "Diferença significativa a 5%" no lugar de "Mudança confirmada"
**Contexto:** "mudança confirmada" sugeria que o teste confirma uma mudança real, relevante ou
explicada. O teste só diz que o IC 95% da diferença entre dois anos não inclui o zero.
**Decisão:** estado interno `SIGNIFICATIVA_5PCT_COM_DECISAO`, selo "Diferença significativa a
5%". O critério não muda: decisão de comparabilidade registrada + evidência nas duas edições +
|d| > 1,96·√(EP₁² + EP₂²). Os estados `SIGNIFICATIVA_SEM_DECISAO` ("aguarda decisão"),
`SIGNIFICATIVA_APROXIMADA` e `NAO_SIGNIFICATIVA` ("pode ser acaso") não mudam. O glossário
explica que significância não é a probabilidade de a mudança ser real e não implica relevância
prática, causa ou ausência de limitações; comparabilidade não implica mudança.

### D24 — Adaptador da PeNSE 2015 Amostra 2 e exclusão por ano
**Decisão:** família `PENSE_2015_A2` (exige "Amostra 2" no rodapé; o 3º nível do código é a
tabela: 2.11.1 ≠ 2.11.10). As famílias de 2024 e 2019 passam a pontuar zero quando o ano do
título/rodapé é outro, para não lerem tabelas de 2015 com a gramática de 2024.

### D25 — "X% de quê?": ficha do número e correção da leitura da tabela 8.1 (2009)
**Contexto:** percentuais como "57%" eram lidos como "% de violências" ou "% de casos
registrados". **Decisão:** cada medida traz, gerado do título/categoria/informante do IBGE
(nunca digitado por indicador): quem são os 100% (`count_base`), quem entra no número
(`situation`), quem respondeu, período e "não confundir com". Para o Tema 17 (diretor), o painel
diz explicitamente que o número é a parcela de ALUNOS em escolas com aquela resposta — não % de
escolas, nem ocorrências, nem boletins, e não implica que o aluno sofreu a violência.
**Correção encontrada:** um rótulo de dimensão de coluna ("Local", tabela 8.1 de 2009) era
tratado como subgrupo ("entre os que faltaram…"). Os números mostram o contrário: "Trajeto"
6,4% e "Escola" 5,5% nas capitais são % de TODOS os escolares do 9º ano (série oficial 10.7/10.8
de 2009: 6,3% e 5,4%). Subgrupo agora só quando o título/grupo o descreve ("Distribuição
percentual…", "Percentual dos escolares que…").

### D26 — Exclusão de uma edição da série principal, por decisão registrada
**Contexto:** uma edição pode ter evidência estatística (reproduz a tabela oficial) e mesmo assim
não ser comparável com as demais por outro motivo — ex.: TRAJETO_INSEGURO, 2015 (Amostra 2)
cobre o 6º ano do EF e 2019/2024 começam no 7º (IBGE 2022, p. 14–16).
**Decisão:** `config/microdata/series_exclusions.csv` (indicador × edição, motivo, evidência,
responsável, data). Sem linha, nada é excluído. Cabeçalho fora do esquema, linha incompleta,
duplicada, com indicador/edição inexistentes, edição que o indicador não tem ou data inválida
ou futura interrompe a pipeline (`SeriesExclusionError`). Texto livre em justificativas nunca
exclui edição. A edição sai só da série principal: as estimativas ficam em
`microdata_estimates.csv` e no painel, marcadas "fora da série principal por decisão
registrada", e o motivo aparece nas ressalvas, em `excluded_edition_ids`/`excluded_editions`
(microdata_comparability.csv), na matriz de evidências (`in_series`) e em
`docs/12_microdados.md` (marca ⊘). A exclusão é separada da decisão de comparabilidade
(`comparability_decisions.csv`), que passa a valer para as edições restantes.

### D28 — Apresentação do IC da diferença entre anos
**Contexto:** o painel mostrava "mudança provável: de 0,0 a 1,7 p.p." para TRAJETO_INSEGURO
2019→2024, cujo limite inferior é +0,0485: o arredondamento a 1 casa escondia que o intervalo
não inclui o zero, e "mudança provável" sugeria leitura probabilística do intervalo.
**Decisão:** texto "IC 95% da diferença: de +0,05 a +1,70 p.p. · o intervalo não inclui o zero"
(ou "inclui o zero: a amostra não permite afirmar que houve diferença"). Casas decimais: o menor
número entre 1 e 4 que não transforma um limite diferente de zero em zero, iguais nos dois
limites, com sinal explícito. A frase vem do mesmo indicador de significância usado pelo selo.
Só apresentação: valores calculados, critério estatístico e CSVs não mudam.

### D29 — Matriz de decisão dos 36 indicadores e registro das propostas aprovadas
**Contexto:** só TRAJETO_INSEGURO tinha decisão registrada; os outros 35 indicadores estavam em
proposta automática. Com os documentos recebidos em 27/10/2026 (questionários do aluno e da
escola de 2019, Manual de Instrução 2019, publicação PeNSE 2024 com Notas técnicas e dicionários),
foi montada uma matriz por indicador: redação, variável e localização (dicionário e questionário)
em 2015, 2019 e 2024; população e período; categorias; regra de não resposta; validação contra
as tabelas oficiais; sensibilidade ao 6º ano para os indicadores com 2015 (Amostra 2);
classificação proposta, justificativa, fontes, limitação residual e recomendação
(`reports/matriz_comparabilidade_2026-10-27/`). As 63 redações de 2015 e 2019 conferem com os
questionários originais.
**Decisão do pesquisador (lista de marcação, 27/10/2026, Caio Justino De Andrade):** aprovadas e
registradas como COMPARABLE_WITH_CAVEATS: bloco A (7 indicadores, série 2015–2019–2024, 2015 só
Brasil e Grandes Regiões), B (ESCOLA_INSEGURA, 2019–2024, com 2015 fora da série principal pelo
mesmo critério de TRAJETO_INSEGURO: a conclusão 2015→2019 muda sem o 6º ano), C (8 indicadores
do aluno, 2019–2024), D (6 indicadores da escola, 2019–2024) e E (9 indicadores do 9º ano, série
oficial 2015–2019, com 2024 fora da série principal até haver tabela oficial para validar).
Texto de TRAJETO_INSEGURO atualizado sem mudar a classificação (técnico/magistério documentado em
2019 e 2024; questão 126 de 2019; Quadro 1 do IBGE 2024). **Não marcado e sem decisão:**
ESCOLA_LOCAL_DROGAS (a proposta automática continua NOT_COMPARABLE). **Pendentes:**
NONO_BRIGA_LUTA_FISICA, NONO_CINTO_FRENTE_OU_TRAS e CAPACETE_AS_VEZES_OU_MAIS.
**Regra mantida:** aprovar a comparabilidade não transforma uma estimativa em validada; cada
registro traz a validação, as ressalvas e as fontes. Estimativas e validações não mudam.
**Correção associada:** a nota da série oficial do 9º ano dizia "regra da tabela oficial não
reproduzida" também quando 2024 sai da série por decisão; agora informa a decisão.
