# Documentos de referência do IBGE

Os originais ficam em `data/reference/` (fora de `data/raw/`, para não serem lidos como
tabelas de dados). `python scripts/build_reference.py` extrai deles os CSVs versionados em
`config/reference/`; `python scripts/build_crosswalk.py` gera a correspondência 2015 × 2024.

| Original | Conteúdo | CSV gerado | Uso na pipeline |
|---|---|---|---|
| `Guia_Tabelas_PeNSE_2024_20260525.xlsx` | catálogo oficial: 1.510 abas em 19 temas (nome da aba e título) | `guia_tabelas_pense_2024.csv` | conferência automática das abas e títulos lidos (`REF001`–`REF003`, relatório `data/processed/reference_check_guia_2024.csv`) |
| `questionario_pense_2015_aluno.pdf` (IBGE doc4595) | questionário do aluno 2015: 151 perguntas com variável, número, texto, opções, pulos e filtros | `questionario_pense_2015_aluno.csv` | texto de origem para tabelas 2015 do aluno e evidência de comparabilidade com 2024 |
| — | cruzamento da seção B9 (Segurança) 2015 com as 23 tabelas do Tema 9 de 2024 | `correspondencia_2015_aluno_x_2024_tema9.csv` | candidatos para série histórica; nunca aprova par sozinho |
| `dicionarios/` (2009, 2012, 2015 A1 e A2, 2019, 2024) | dicionários de microdados do IBGE: variável, pergunta, códigos, posição (largura fixa) | `dicionario_<EDIÇÃO>.csv` (`scripts/build_dictionaries.py`) | texto da pergunta de origem, comparação de redação entre edições, leitura de 2009/2012 |
| `dicionarios/Exemplo_calculo_*.txt` | exemplos oficiais de estimação (R `survey`, SAS `SURVEYMEANS`) | — | confirmam o desenho implementado (UPA escola, estrato, pós-estratificação, domínio `IND_EXPANSAO = 1`) |
| `Nota_tecnica_01_2022_confidencialidade_PeNSE2019.pdf` | controle de confidencialidade dos microdados 2019 | — | explica as diferenças em recortes restritos; critério de validação de 2019 |
| `PeNSE_2019_publicacao.pdf` (Manual de Instrução 2019) | desenho amostral (53 estratos geográficos × dependência), CV de dimensionamento 4% | — | metodologia do TCC |
| `Guia_Tabelas_PeNSE_2019_20260615.xls`, `Guia_Tabelas_PeNSE_2009_2019_9ano.xls` | catálogos oficiais das tabelas de 2019 e da série do 9º ano | — | referência |
| `liv101955_PeNSE_indicadores_comparaveis_9ano_2009_2019.pdf` (IBGE, Estudos e Pesquisas n. 46, 2022) | análise dos indicadores comparáveis do 9º ano nas capitais; notas técnicas de harmonização (p. 18–20); glossário | — | **fonte da convenção de não resposta da série** (sem resposta × abandono, p. 18, nota 7; D21); Quadro 2 de variáveis de desenho (comparado na D22); definição do indicador 10.3 (glossário, p. 120–122); aviso de **estatística experimental** |
| `Nota_metodologica_01_utilizacao_microdados_2015.pdf` | uso dos microdados 2009–2015; Quadro 3 (UPA, estrato, peso) | — | desenho de 2009, 2012 e 2015 (D22) |
| `Nota_metodologica_02_…_Amostra_1_2015.pdf`, `Nota_metodologica_03_…_Amostra_2_2015.pdf` | especificação das tabelas de 2015 (numerador, denominador) | — | regras dos indicadores de 2015; convenção da publicação (99 fora) |
| `tema01/Amostra_2_Tema_01_Informacoes_Gerais_2015.xls`, `tema01/Tema_01_Informacoes_Gerais_XLSX_20260525.zip` | totais e características gerais (2015 A2 e 2024) | — | conferência dos pesos: soma dos pesos 2015 A2 = 13.199.861,8 (igual à 2.1.1); 2024 difere da 1.1.1 em 276 escolares (0,002%) |

## Resultado da conferência com o guia 2024

As 156 abas de 2024 lidas (Tema 9: 138; Tema 17: 18) estão todas no guia, nenhuma aba
dos dois temas falta nos arquivos e os 156 títulos extraídos são iguais aos do guia
(comparação sem acentos, espaços e prefixo "Tabela x.y.z -").

## Como o questionário foi lido

O PDF tem duas colunas e usa cores com significado (legenda na página 1): **vermelho** =
questão alterada em relação à edição anterior, **verde** = questão nova, **azul** = pulos,
filtros, críticas e alertas. O extrator usa a cor e a posição reais de cada palavra
(pdfplumber): a cor do código da variável vira `change_vs_previous` (ALTERADA / NOVA /
MANTIDA) e o texto azul vai para `filters_and_checks`. A seção B9 (18 perguntas) foi
conferida contra as páginas 15–17 do PDF e é verificada em `tests/test_reference.py`.

## Ressalvas importantes

* As tabelas de 2015 já processadas (Amostra 1, Tema 6 "Segurança da escola") vêm do
  **questionário da escola**, não deste questionário do aluno; por isso este documento ainda
  não preenche `question_text` dessas observações.
* O questionário de 2015 serve às amostras 1 (9º ano) e 2 (13 a 17 anos); algumas perguntas
  só valem para a amostra tipo 2 (ex.: B09016 é pulada para menores de 13 anos).
* A correspondência 2015 × 2024 é leitura dos textos oficiais: 7 pares de **mesmo conceito
  candidato**, 8 **próximos com diferenças**, 4 **conceitos diferentes** (período ou agressor
  diferentes) e 7 sem correspondente. Todos ficam `A_VALIDAR_PELO_PESQUISADOR` até haver o
  questionário 2024 e tabelas 2015 da Amostra 2.
