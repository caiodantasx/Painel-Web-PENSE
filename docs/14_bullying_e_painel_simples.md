# Bullying, série histórica 2015–2019–2024 e painel simples (nov/2026)

Registro do que foi feito em 07/11/2026 para responder à consulta com 5 gestores escolares (RN e PB).
Eles pediram, nesta ordem: indicadores de bullying (sofrido 5/5, praticado 4/5, cyberbullying 3/5),
filtros simples, mapa, linguagem simples e série histórica. Também fizeram duas perguntas abertas:
"quantos estudantes do meu território foram vítimas e de quais tipos?" e "os estudantes faltam por medo de bullying?".

## 1. Dados novos

| Arquivo em `data/raw/` | Origem | Uso |
|---|---|---|
| `Tema_02_Situacoes_em_Casa_e_na_Escola_XLSX_20260525.zip` | IBGE, PeNSE 2024 (zip recebido do usuário) | tabelas 2.1 a 2.15 de 2024 (bullying: 2.5 a 2.10, 2.13 a 2.15) |
| `Tema_02_Situacoes_em_Casa_e_na_Escola_2019_20260615.xls` | `ftp.ibge.gov.br/pense/2019/xls/` (baixado em 07/11/2026) | validação de 2019 (2.5, 2.9, 2.10) |
| `Amostra_2_Tema_07_Situacoes_em_Casa_e_na_Escola_2015.xls` | `ftp.ibge.gov.br/pense/2015/xls/` (baixado em 07/11/2026) | validação de 2015 Amostra 2 (2.7.9) |

Os três arquivos são lidos pelos adaptadores que já existiam (mesmas famílias dos Temas 9, 11 e 17), sem código novo de leitura.
Conferência do Brasil em 2024: 2.5 "duas ou mais vezes" = 27,2%; 2.9 = 12,7%; 2.10 = 13,7%; 2.15 = 10,0%.

**Defeito do IBGE registrado pelo validador:** na planilha de 2019, a aba 2.6.3 (motivos, capitais) traz no rodapé
"Pesquisa Nacional de Saúde do Escolar, Amostra 1, 2015". A regra VAL013 (ano do título ≠ ano do rodapé) marca os
196 valores dessa aba como ERRO e eles ficam fora da análise. A aba não é usada no painel.

## 2. Indicadores recalculados pelos microdados (`config/microdata/indicators.toml`)

| Chave | Pergunta | Edições | Validação contra a tabela publicada |
|---|---|---|---|
| `BULLYING_SOFREU` | humilhado por colegas **2 ou mais vezes** (2019 `B07007A` = 3; 2024 `B07007B` ∈ {3, 4}) | 2019, 2024 | 2019: 2.5, com ressalva (máx. 0,42 p.p.) · 2024: 2.5, validado |
| `BULLYING_PRATICOU` | zombou ou intimidou colega (`VB07009`/`B07009` = 1) | 2015 A2, 2019, 2024 | 2015: 2.7.9, 42/42 exatos · 2019: 2.10, com ressalva · 2024: 2.10, validado |
| `CYBER_SOFREU` | ameaçado ou humilhado nas redes (`B07013` = 1) | 2019, 2024 | 2019: 2.9, com ressalva · 2024: 2.9, validado |
| `CYBER_PRATICOU` | ameaçou ou humilhou nas redes (`B07016` = 1) | 2024 | 2.15, validado |
| `FALTOU_INSEGURANCA_SOFREU_BULLYING` / `…_NAO_SOFREU_…` | faltou por insegurança na escola (`B09002`), entre quem sofreu bullying 2+ vezes e quem não sofreu nenhuma vez | 2024 | sem tabela publicada (cruzamento do projeto) |
| `ALGUMA_VIOLENCIA` | bullying 2+ ou cyberbullying (30 dias), ou agressão física por pais ou por outra pessoa (12 meses) | 2024 | sem tabela publicada (indicador composto do projeto) |

O "com ressalva" de 2019 é o mesmo de todos os indicadores dessa edição: os microdados públicos de 2019 têm controle de
confidencialidade (Nota técnica 01/2022). Os totais do Brasil reproduzem a tabela, e há diferenças pequenas em alguns recortes.

O campo novo `given` em `indicators.toml` restringe numerador e denominador a um subgrupo, por exemplo quem sofreu bullying.
A PeNSE não pergunta o motivo da falta, então o bloco "bullying × faltas" mostra **associação, não causa**, e a tela diz isso.

## 3. Série histórica e decisões de comparabilidade

Decisões em `config/microdata/comparability_decisions.csv`, registradas em 07/11/2026 a pedido explícito do pesquisador
("deixe a série histórica 2024-2019-2015 pronta pra comparação"). O texto foi preparado com assistência de IA e está sujeito a revisão.

| Indicador | Série | Por quê | Resultado (Brasil) |
|---|---|---|---|
| Bullying praticado | **2015 · 2019 · 2024** (2015 só Brasil e regiões) | mesma variável e redação nas três edições; validado nas três; sensibilidade ao 6º ano **robusta** | 20,3% → 12,0% → 13,7%: caiu 8,2 p.p. de 2015 a 2019 [−9,5; −7,0] e subiu 1,6 p.p. de 2019 a 2024 [+0,8; +2,4] |
| Bullying sofrido (2+ vezes) | **2019 · 2024** | mesma redação; opções detalhadas em 2024, e "2 ou mais" é publicado pelo IBGE nas duas edições. 2015 fica de fora: escala sem contagem de vezes | 23,0% → 27,2%: subiu 4,2 p.p. [+3,4; +5,0] |
| Cyberbullying sofrido | **2019 · 2024** | mesma variável e redação; não existia em 2015 | 13,2% → 12,7%: diferença de −0,5 p.p. [−1,1; +0,1], dentro da margem de erro |
| Cyberbullying praticado | só 2024 | pergunta nova | — |

**Sensibilidade ao 6º ano (2015).** A Amostra 2 de 2015 incluiu turmas do 6º ano, e 2019 e 2024 começam no 7º. O peso do 6º ano no
denominador de 2015 é 2,98%. Retirando-o, a queda 2015→2019 do bullying praticado continua significativa (−7,99 p.p.
[−9,29; −6,70]). Método idêntico ao da matriz de 27/10/2026. Script e resultado em `reports/serie_bullying_2026-11-07/`.

**Ressalvas que valem para todas as séries:** desenhos amostrais próprios de cada edição; regra de não resposta confirmada por
reprodução das tabelas (lacuna documental já registrada para os outros indicadores); comparabilidade não é o mesmo que mudança;
significância não indica causa nem relevância prática. Específicas: a escala de respostas do bullying sofrido mudou; o contexto
das redes sociais mudou entre 2019 e 2024; a queda grande do bullying praticado de 2015 a 2019 pode refletir também a posição da
pergunta no questionário (efeito de contexto não testável).

## 4. "Cerca de N estudantes"

O número de estudantes é o percentual publicado vezes o total estimado de escolares de 13 a 17 anos do lugar e do grupo.
Esse total é a soma dos pesos amostrais do denominador nos microdados, coluna `w` do pacote. A faixa usa os limites do IC do
percentual e trata o total como conhecido: os pesos de 2024 são pós-estratificados para totais de matrícula. Para itens sem
indicador próprio nos microdados, usa-se o total de `BULLYING_SOFREU`, que corresponde a todos os escolares menos os abandonos
de questionário. Nos motivos (2.6 e 2.13), a base é quem sofreu ou quem praticou, porque as categorias somam mais de 100%.
Por isso a contagem ali é aproximada (produto de duas estimativas) e aparece sem faixa.

A PeNSE não tem dados por município, só por capital, e não tem dados por escola. A tela diz isso e oferece estado e capital.

## 5. Painel

* **Painel** (página inicial): três escolhas (Onde? · Sobre o quê? · Quais alunos?) e o mapa no topo. Ao lado, a resposta
  principal em "X em cada 100", com a margem de erro como "entre A% e B%", a comparação com o Brasil já interpretada (maior, menor
  ou parecido, pela sobreposição dos IC) e "cerca de N estudantes". Também na página: cartões de bullying e de algum tipo de
  violência, tipos do mais ao menos comum, "Mudou com o tempo?" com veredito, e bullying × faltas.
  Em cada número: Ver no IBGE · Baixar dados · Como ler.
* **Estimativas**: quantos estudantes sofreram ou praticaram bullying, foram agredidos, brigaram ou faltaram, com faixa;
  motivos do bullying; CSV do lugar.
* As páginas anteriores continuam acessíveis como "Detalhes": Mapa e tabelas, Territórios, Série histórica, Qualidade e Sobre.
* As ligações entre frases e medidas ficam em `config/painel_gestor.toml`, exportadas por `src/pense/exports/gestor.py`.
  Nenhum número fica escrito no JavaScript.

## 6. Fora desta versão

* Reconferir com o pesquisador o texto das três decisões de comparabilidade (registradas a pedido dele em 07/11/2026).
* Série de bullying sofrido com 2015 (escala diferente) e série dos motivos (2.6/2.13).
* Validar o rótulo "Os 100% são" das tabelas por motivo nas páginas de detalhe: a leitura automática diz "escolares de 13 a 17 anos",
  mas a base real é quem sofreu ou quem praticou (a página Estimativas já usa a base certa).
