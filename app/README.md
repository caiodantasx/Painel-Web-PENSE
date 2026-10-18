# Dashboard PeNSE 2024 — protótipo visual

## Como executar
1. Extraia a pasta/ZIP.
2. Abra o terminal nessa pasta.
3. Execute `python -m http.server 8000`.
4. Acesse http://localhost:8000

## Atenção sobre os dados
Esta versão reproduz o estilo da imagem, com filtros interativos, cartões KPI, mapa esquemático, gráficos, tabela e exportação CSV. Os números são **ilustrativos** e não devem ser usados como resultados do IBGE. Os filtros alteram a interface para demonstrar o comportamento, mas ainda não fazem uma consulta real às tabelas PeNSE. O mapa é esquemático e não corresponde às fronteiras oficiais.

Para a versão acadêmica, precisamos vincular cada indicador aos valores extraídos das tabelas oficiais, validar IC95%, população, desagregações e equivalência entre 2019 e 2024.

O gráfico usa Chart.js via CDN; para funcionar, o navegador precisa de conexão à internet na primeira abertura.
