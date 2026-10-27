# Manual do painel

Abra com `python -m http.server -d dashboard 8000` e acesse `http://localhost:8000`.
O painel lê `dashboard/data/pense_bundle.json` (gerado pela pipeline),
`dashboard/assets/geo/br_uf.json` (malha das UFs) e `dashboard/assets/geo/capitais.json`
(posição aproximada da sede de cada capital, só para desenhar o marcador). Não há
estimativas escritas no JavaScript.

## Filtros (linha superior)

| Filtro | Comportamento |
|---|---|
| Edição | PeNSE 2024, 2015 (Amostra 1) ou 2009 |
| Indicador | famílias de tabela da edição, com rótulo curto (`config/indicator_labels.csv`) |
| Categoria | tipos de violência, banco, agressor, etc.; desativado quando há uma só |
| Medida | aparece só quando a tabela tem contagem e percentual (2015) |
| Idade, sexo, dependência | opções não publicadas para a combinação atual aparecem como "indisponível" |

Se uma combinação deixa de existir após trocar o indicador, os filtros voltam para Total
e um aviso explica o motivo.

## Páginas

* **Visão geral:** abre com o **mapa do Brasil**. O seletor do mapa troca o recorte
  territorial entre *Estados (UF)* (coroplético), *Capitais* (marcador colorido na sede
  de cada capital) e *Regiões* (cada UF pintada com o valor da sua Grande Região); recortes
  que a tabela não publica aparecem riscados e desativados (ex.: 2009 só tem capitais).
  Ao lado do mapa: estimativa de referência (Brasil ou conjunto das capitais) com IC e CV,
  cartão de comparação do território clicado (diferença em p.p., sem teste de
  significância) e os cinco maiores e menores valores. Abaixo: ranking em tabela com
  barras, IC 95% e linha tracejada da referência (ordenável por maior, menor ou A–Z),
  gráficos por categoria e por recorte populacional, definição completa e cobertura.
  Mapa, cartões e ranking ficam sincronizados pela seleção.
* **Territórios:** ranking em gráfico com IC 95% e tabela com arquivo, aba e célula de
  origem de cada valor.
* **Série histórica:** abre com o panorama da **série harmonizada pelos microdados**
  (2015 Amostra 2, 2019, 2024): uma linha por indicador com os valores do Brasil, mini
  gráfico, última variação e se ela é significativa a 5%, e o status de comparabilidade.
  Clicar numa linha abre o detalhe: indicador, território (Brasil, regiões; UFs e capitais
  em 2019–2024) e recorte (idade, sexo, dependência); gráfico com faixa do IC 95%,
  cartões de variação entre anos com IC da diferença, evidências de comparabilidade,
  ressalvas, conferência com as tabelas do IBGE e método. Indicadores pendentes de revisão
  mostram os pontos **sem** linha de tendência. Todo valor dessa seção leva o selo
  "Calculado dos microdados". Abaixo, a situação das **tabelas publicadas** e a tabela de
  pares avaliados.
* **Qualidade:** status das observações do indicador, alertas por regra na base inteira,
  lista das observações com ressalva, revisão ou indisponíveis.
* **Sobre os dados:** método, edições, símbolos, dicionário de dados e download da base
  aprovada (versão publicada).

## Edição exibida e "X% de quê?"

**Por que o painel abre em 2024?** É uma decisão de projeto: a Visão geral mostra **uma edição
por vez**, começando pela mais recente, porque cada edição entrevistou um público diferente (9º
ano em 2009 e 2015 Amostra 1; 13 a 17 anos em 2015 Amostra 2, 2019 e 2024) e cobre territórios
diferentes. As outras edições ficam na faixa **"Ano da pesquisa"** logo acima do mapa (e no
filtro de mesmo nome). A evolução no tempo, só com indicadores comparáveis, fica na página
**Série histórica**.

**Ficha "Como ler este número"** (ao lado do mapa e no quadro de definição), gerada pela pipeline
a partir do título, da categoria e do informante publicados pelo IBGE (`src/pense/exports/reading.py`):

| Linha | Exemplo (17.1, 2024, Brasil) |
|---|---|
| Quanto é | 28,4% = cerca de 28 em cada 100 escolares de 13 a 17 anos — Brasil |
| Os 100% são | todos os escolares de 13 a 17 anos — Brasil |
| Entram no número os que | estudam em escolas cujo diretor presenciou ou ouviu falar de “Assaltos e roubos…” na localidade da escola |
| Quem respondeu | o diretor(a) ou responsável pela escola |
| Período | 12 meses anteriores à pesquisa |
| Não confundir com | não é % de escolas, nem número de ocorrências, nem boletim de ocorrência; não significa que esses alunos sofreram ou viram a violência |

Abaixo de 10%, o "quanto é" vira "cerca de 1 em cada N" (ex.: 5,2% = cerca de 1 em cada 19).
Listas, tabela e legenda do mapa dizem a unidade ("valores em % dos escolares de 13 a 17 anos").
Os rótulos de "O que é medido" dos indicadores do Tema 17 dizem "relatada pelo diretor".

## Série histórica: o que cada selo quer dizer

| Selo | Significado |
|---|---|
| **Diferença significativa a 5%** | o pesquisador registrou a decisão de que os anos são comparáveis, as duas edições foram conferidas com tabelas do IBGE e o IC 95% da diferença não inclui o zero. Não quer dizer que a diferença é grande, importante ou explicada |
| **Significativa · aguarda decisão** | a diferença é significativa, mas a comparação ainda é só uma proposta automática |
| **Significativa (teste aproximado)** | série oficial do 9º ano entre anos publicados (erro-padrão derivado da margem de erro; série experimental do IBGE) |
| **Pode ser acaso da amostra** | diferença não significativa |
| **IC 95% da diferença** | abaixo de cada variação: "de +0,05 a +1,70 p.p. · o intervalo não inclui o zero". Usa o menor número de casas (1 a 4) que não mostra como "0,0" um limite diferente de zero (D28). O texto vem do mesmo indicador de significância que o selo |
| **proposta automática / decisão registrada** | abaixo do selo "Pode comparar os anos?" |
| **†** | ano fora da série: sem tabela do IBGE para conferir o cálculo (o valor continua visível no detalhe) |

Em 2015 o detalhe mostra o valor com a regra da série e, ao lado, o valor publicado pelo IBGE
naquele ano (convenção de não resposta diferente; D21).

## Linguagem e ajuda

O painel evita jargão: "margem de erro" (intervalo de confiança de 95%), "precisão" boa /
razoável / baixa (coeficiente de variação < 15%, 15–30%, ≥ 30%), "situação do número"
(Confiável, Usar com cuidado, Em revisão, Sem valor publicado), "diferença significativa a 5%"
(com decisão registrada). O glossário "Como ler os números" fica sob os filtros
(fechado por padrão) e todo "?" abre a explicação do termo por mouse ou teclado. A página
Qualidade traz a legenda dos níveis de alerta (Informativo, Ressalva, Revisão, Erro). O CSV
exportado usa cabeçalhos legíveis em português, com precisão e situação por extenso. A página
"Sobre os dados" mantém os termos técnicos, para quem precisa deles.

## Convenções visuais

* Tema escuro sempre por padrão (preto azulado com azul e roxo), inclusive com o sistema em
  modo claro; o tema claro só aparece se o visualizador escolher explicitamente.
* Barras azuis: estimativas; magenta: selecionado; cinza: Brasil/referência. O par
  azul–magenta foi validado para daltonismo (ΔE ≥ 14 em protanopia); azul e roxo ficam
  só na identidade visual, porque não se distinguem bem como cores de dados.
* Mapa: rampa sequencial de um só tom (índigo), 5 classes de amplitude igual.
* Barra mais clara e "‡": precisão baixa (CV ≥ 30%).
* Traço fino com pontas sobre a barra: margem de erro publicada.
* Status sempre com forma + texto (círculo = válido, losango = ressalva, quadrado =
  revisão, triângulo = erro).

## Exportação

"Exportar seleção (CSV)" baixa os territórios do recorte atual com estimativa, IC, CV,
status, regras e célula de origem (separador `;`, vírgula decimal). Onde o download for
bloqueado, "Copiar CSV" copia o mesmo conteúdo.

## Acessibilidade e responsividade

Navegação por teclado (Tab/Enter em abas, barras, mapa e linhas de tabela), foco visível,
rótulos em todos os controles, tooltips também por foco, tabela como alternativa a todo
gráfico, temas claro e escuro, layout de uma coluna a partir de 360 px, respeito a
`prefers-reduced-motion` e `forced-colors`.
