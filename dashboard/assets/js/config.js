/* Constantes e textos fixos do painel: recortes territoriais, rótulos de status,
 * explicação das regras de validação e o glossário dos ícones “?”. */
"use strict";

const SVGNS = "http://www.w3.org/2000/svg";
const APPROVED = new Set(["VALID", "VALID_WITH_WARNINGS"]);
const SCOPES = {
  uf: { label: "Unidades da Federação", short: "Estados (UF)", types: ["uf"], ref: "BR" },
  capital: { label: "Municípios das capitais", short: "Capitais", types: ["capital"], ref: "CAPITAIS" },
  regional: { label: "Brasil e Grandes Regiões", short: "Regiões", types: ["country", "region"], ref: "BR" },
};
const SCOPE_PREF = ["uf", "capital", "regional"];
const STATUS_LABEL = {
  VALID: ["Confiável", "good"], VALID_WITH_WARNINGS: ["Usar com cuidado", "warning"],
  REVIEW_REQUIRED: ["Em revisão", "serious"], ERROR: ["Erro", "critical"], NOT_AVAILABLE: ["Sem valor publicado", "neutral"],
};
const COMP_LABEL = {
  COMPARABLE: ["Comparável", "good"], COMPARABLE_WITH_CAVEATS: ["Comparável com ressalvas", "warning"],
  NOT_COMPARABLE: ["Não comparável", "critical"], PENDING_REVIEW: ["Pendente de revisão", "serious"],
  SEM_CORRESPONDENTE_IDENTIFICADO: ["Sem correspondente", "neutral"],
};
// Estado da diferença entre dois anos, decidido pela pipeline (src/pense/microdata/series.py):
// o selo "Diferença significativa a 5%" só existe com decisão registrada do pesquisador e evidência
// nas duas edições (D27). Significância não é relevância prática nem causa.
const CHANGE_LABEL = {
  SIGNIFICATIVA_5PCT_COM_DECISAO: ["Diferença significativa a 5%", "good"],
  SIGNIFICATIVA_SEM_DECISAO: ["Significativa · aguarda decisão", "warning"],
  SIGNIFICATIVA_APROXIMADA: ["Significativa (teste aproximado)", "warning"],
  NAO_SIGNIFICATIVA: ["Pode ser acaso da amostra", "neutral"],
};

const RULE_TEXT = {
  VAL001: "o IBGE publicou um símbolo (ex.: “-”) no lugar do número",
  VAL002F: "arredondamento do computador na planilha (ex.: 100,0000000001%), valor mantido",
  VAL002N: "o limite inferior da margem de erro publicada ficou abaixo de 0%",
  VAL005: "margem de erro publicada igual a zero, comum em grupos com pouquíssimas escolas",
  VAL006: "margem de erro cortada em 0% ou 100% (o valor real não pode passar desses limites)",
  VAL008: "estimativa pouco precisa: a margem de erro é grande em relação ao valor",
  VAL009: "margem de erro e precisão publicadas não batem entre si",
  VAL012: "nome de lugar não reconhecido na lista de territórios",
  VAL014: "as categorias somadas não dão 100%",
  VAL015: "o total ficou fora da faixa das partes (ex.: total menor que meninos e meninas)",
  VAL020: "o mesmo número aparece diferente em duas tabelas",
  VAL022: "cabeçalho da tabela ambíguo: precisa de conferência humana",
  OUT001: "valor muito diferente dos outros lugares (pode ser real, só sinalizado)",
  VAL002: "percentual fora de 0 a 100", VAL003: "limites da margem de erro invertidos",
  VAL004: "o valor ficou fora da própria margem de erro", VAL007: "margem de erro com só um dos limites",
  VAL010: "o valor difere entre a aba principal e a aba de precisão do IBGE",
  VAL011: "a mesma linha aparece duas vezes na tabela", VAL013: "o ano do título difere do ano da fonte",
  VAL016: "texto no lugar do número", VAL017: "erro do Excel na célula", VAL018: "contagem negativa",
  VAL019: "o total não é a soma das partes", VAL021: "seção da tabela não reconhecida",
  VAL023: "o mesmo recorte aparece na linha e na coluna", VAL024: "ano lido da coluna da tabela (série com vários anos)",
  VAL025: "ano não identificado na tabela",
  HDR001: "coluna que a leitura automática não entendeu", HDR005: "cabeçalho deduzido sem células mescladas",
  HDR006: "cabeçalho da tabela ambíguo", STB004: "linha de seção com números repetidos (defeito da planilha), ignorada",
  STB005: "linha de seção com números próprios, não usada",
  NRM003: "sem correspondente na aba de precisão", NRM004: "linha da aba de precisão sem valor principal",
  ING008: "caminho suspeito dentro do ZIP", ING010: "arquivo que não pôde ser lido",
  ADP000: "aba sem leitor reconhecido", ADP900: "falha do leitor da tabela",
  REF001: "tabela do guia oficial que não veio nos arquivos", REF002: "título diferente do guia oficial do IBGE",
  REF003: "aba que não está no guia oficial",
};
const ISSUE_CLASS = {
  ERRO_CONFIRMADO: "erro confirmado", POSSIVEL_ANOMALIA: "pode ser problema", POSSIVEL_VALOR_EXTREMO_LEGITIMO: "valor extremo, provavelmente real",
  NAO_VALIDADO: "ainda não conferido", INFORMATIVO: "só registro",
};
// Glossário: um texto por termo, usado nos ícones “?” de todo o painel.
const GLOSS = {
  margem: "Margem de erro (intervalo de confiança de 95%): a PeNSE entrevista uma amostra de alunos, não todos. Por isso cada número é uma estimativa, e a margem mostra a faixa onde o valor real provavelmente está. Ex.: 12% (entre 11% e 13%).",
  precisao: "Precisão (coeficiente de variação, CV): o tamanho da margem de erro em relação ao valor. Boa: CV abaixo de 15%. Razoável: de 15% a 30%. Baixa: 30% ou mais — use o número só como indicação.",
  comparar: "Para dizer que um lugar tem valor maior que outro, as margens de erro não devem se sobrepor muito. Diferenças pequenas com margens sobrepostas podem ser só efeito da amostra.",
  significativa: "Diferença significativa a 5%: o intervalo de confiança de 95% da diferença entre os dois anos não inclui o zero. Em outras palavras, se não houvesse diferença nenhuma entre os anos, uma diferença deste tamanho ou maior apareceria em menos de 5% das amostras possíveis. Isso não é a chance de a mudança ser real, e um resultado significativo não é certeza absoluta. Significativa não quer dizer grande nem importante, não explica a causa e não elimina outras limitações (mudança de pergunta, de público ou de método). “Não significativa” não quer dizer que nada mudou, só que a amostra não permite afirmar. O selo “Diferença significativa a 5%” só aparece quando o pesquisador registrou a decisão de que os anos são comparáveis e as duas edições foram conferidas com as tabelas do IBGE; antes disso, a diferença aparece como “aguarda decisão”. Ser comparável não quer dizer que houve mudança.",
  pp: "Pontos percentuais (p.p.): diferença entre dois percentuais. De 10% para 13% é um aumento de 3 p.p. (e não de 3%).",
  indicador: "Indicador: o que está sendo medido, sempre como percentual dos escolares (ou da escola) que responderam de certa forma.",
  edicao: "Ano da pesquisa (edição): a PeNSE foi feita em 2009, 2012, 2015, 2019 e 2024. Cada edição tem um público diferente (9º ano ou 13 a 17 anos), por isso nem todas podem ser comparadas.",
  recorte: "Recorte: um grupo de alunos dentro do total — faixa de idade, sexo ou rede de ensino (pública ou privada).",
  situacao: "Situação do número: Confiável (passou em todas as verificações), Usar com cuidado (passou, mas tem uma observação), Em revisão (fora dos gráficos até alguém conferir), Sem valor publicado (o IBGE publicou um símbolo).",
  origem: "Onde o número está na planilha original do IBGE (arquivo, aba e célula), para quem quiser conferir.",
  n: "n: número de alunos que responderam à pergunta nesse grupo. Grupos pequenos têm margens de erro maiores.",
  microdados: "Calculado dos microdados: o número não está numa tabela publicada; foi calculado a partir das respostas individuais divulgadas pelo IBGE, com o mesmo método oficial e conferido contra as tabelas que existem.",
};
