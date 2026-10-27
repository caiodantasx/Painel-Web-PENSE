# Relatório de testes

Execução: 27/10/2026 18:53 · Python 3.13.17 · comando `python -m pytest` · tempo 48.1 s

**Resultado: 224 aprovados, 0 falhas, 0 pulados.**

| Módulo de teste | Aprovados | Falhas | Pulados | O que cobre |
|---|---|---|---|---|
| `test_adapters_regression` | 7 | 0 | 0 | valores reais conferidos célula a célula nas quatro famílias, junção do CV, cobertura de todas as abas |
| `test_apresentacao_ic` | 14 | 0 | 0 | IC da diferença no painel (D28): limite perto de zero nunca vira 0,0, frase coerente com o teste e o selo, sem 'mudança provável', arquivos citados nas decisões existem |
| `test_correcoes_2026_10` | 19 | 0 | 0 | adaptador 2015 A2, convenções de não resposta (abandono × sem resposta), proposta × decisão, edições sem evidência fora da série, recálculo real dos microdados contra tabelas publicadas |
| `test_dashboard_e2e` | 12 | 0 | 0 | painel sem erros, mapa como primeiro painel, clique no mapa sincroniza ranking, recortes indisponíveis desativados, valores vindos da base, teclado/rótulos, 360 px sem rolagem lateral |
| `test_exclusao_edicao` | 31 | 0 | 0 | exclusão de edição da série principal por decisão registrada (D26): padrão sem exclusão, série 2019–2024 de TRAJETO_INSEGURO, sem comparação 2015→2019, dados de 2015 preservados, configuração inválida interrompe, demais indicadores intactos |
| `test_harmonization_historical` | 9 | 0 | 0 | comparabilidade conservadora, decisão humana com justificativa, série só para pares aprovados, média descritiva |
| `test_ingestion` | 9 | 0 | 0 | ZIP em memória, duplicatas por hash, zip slip, ZIP corrompido/aninhado, leitores XLSX/XLS/CSV/ODS |
| `test_microdata` | 10 | 0 | 0 | estimador de desenho (fórmula fechada, domínio, pós-estratificação), diferença entre anos, regras de comparabilidade, reprodução das tabelas publicadas 2024 e 2019 |
| `test_multiyear` | 5 | 0 | 0 | tabelas com vários anos: ano por coluna/seção (inclusive 2009.0 do .xls), título com lista de anos, valor sem ano vai para revisão |
| `test_parsing` | 30 | 0 | 0 | título, período, população, escopo, cabeçalho multinível por mesclagem, CSV sem mesclagem, stub, territórios |
| `test_pipeline_integration` | 8 | 0 | 0 | pipeline ponta a ponta, falha isolada, rastreabilidade até a célula, camada aprovada, idempotência, CSV |
| `test_reading` | 8 | 0 | 0 |  |
| `test_reference` | 4 | 0 | 0 | guia oficial 2024 (1.510 abas, 19 temas), questionário do aluno 2015 conferido com o PDF, conferência de abas e títulos (REF001–REF003) |
| `test_rotulo_significancia` | 19 | 0 | 0 | selo 'Diferença significativa a 5%' (D27): só com decisão registrada e significância, critério estatístico inalterado, estados preservados, mesmos nomes no CSV/painel/relatório, glossário sem a leitura de probabilidade |
| `test_text` | 24 | 0 | 0 | normalização de textos e valores, símbolos, números pt-BR, erros do Excel |
| `test_validation` | 15 | 0 | 0 | todas as regras de qualidade, status, preservação de valores, nunca remover observações |

## Verificações de dados na última execução da pipeline

| Regra | Avaliações |
|---|---|
| OUT001 | 22795 |
| VAL002 | 99304 |
| VAL003/VAL004 | 33100 |
| VAL008 | 12428 |
| VAL009 | 12128 |
| VAL011 | 33220 |
| VAL014 | 465 |
| VAL015 | 15066 |
| VAL019 | 74 |
| VAL020 | 1728 |
| VAL010 | 12459 |
| REF_abas_conferidas | 156 |
| REF_temas | 2 |
| REF_titulos_iguais | 156 |
| QST_perguntas_ligadas | 22864 |
