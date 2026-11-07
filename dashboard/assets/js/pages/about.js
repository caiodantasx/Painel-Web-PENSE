/* Página “Sobre os dados”: método, edições, símbolos e dicionário de dados. */
"use strict";

function renderAbout() {
  const box = clear($("about-method"));
  box.append(
    el("h2", { text: "Como os números chegam aqui" }),
    el("p", { text: "As tabelas oficiais do IBGE (XLS, XLSX e ZIP) são lidas por uma pipeline em Python. Cada família de tabela tem um adaptador que interpreta o cabeçalho pelas células mescladas, identifica estimativa, limites do intervalo de confiança de 95% e coeficiente de variação, e registra arquivo, aba e célula de cada valor." }),
    el("h3", { text: "Validação" }),
    el("p", { text: "Regras determinísticas conferem percentuais fora de 0–100, intervalos invertidos, estimativa fora do IC, coerência entre CV e IC, somas de distribuições, totais entre as partes e valores iguais publicados em tabelas diferentes. Valores incomuns são sinalizados, nunca removidos." }),
    el("h3", { text: "Leitura correta" }),
    el("ul", null,
      el("li", { text: "Diferenças entre territórios ou grupos só são discutíveis olhando os intervalos de confiança; este painel não executa testes de significância." }),
      el("li", { text: "CV ≥ 30% indica baixa precisão (barra mais clara e símbolo ‡)." }),
      el("li", { text: "Os cruzamentos de idade, sexo e dependência administrativa dependem da tabela publicada; combinações que o IBGE não publica aparecem como indisponíveis nos filtros, nunca estimadas." }),
      el("li", { text: "Para contagens (estimativa total de escolares), o mapa é desativado: totais absolutos refletem o tamanho da população." }),
      el("li", { text: "As edições 2009 e 2015 referem-se a escolares do 9º ano; a de 2024, a escolares de 13 a 17 anos. Por isso não são combinadas em série." })),
    el("h3", { text: "Exportação" }),
    el("p", { text: "O botão Exportar gera um CSV da seleção atual (todos os territórios do recorte, com status e célula de origem), separado por ponto e vírgula e com vírgula decimal para abrir direto no Excel em português." }),
  );
  table($("table-editions"), [
    { label: "Edição", render: (e) => `PeNSE ${e.reference_year}` },
    { label: "População", render: (e) => e.target_population },
    { label: "Cobertura", render: (e) => e.territorial_coverage },
    { label: "Observação", render: (e) => e.notes },
  ], B.meta.editions);
  table($("table-symbols"), [
    { label: "Símbolo", cls: "mono", render: (s) => s.symbol }, { label: "Significado", render: (s) => s.meaning },
    { label: "Tratamento", render: (s) => s.treatment },
  ], B.symbols);
  table($("table-dictionary"), [
    { label: "Campo", cls: "mono", render: (d) => d.field }, { label: "Tipo", cls: "mono", render: (d) => d.type },
    { label: "Descrição", render: (d) => d.description }, { label: "Origem", render: (d) => d.origin },
  ], B.dictionary);
}
