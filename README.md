# PeNSE em Painel

Painel web de dados abertos sobre **violência e segurança no ambiente escolar**, construído a partir das tabelas oficiais da **Pesquisa Nacional de Saúde do Escolar (PeNSE)** do IBGE, edições **2019** e **2024**.

Trabalho de Conclusão de Curso — *PeNSE em Painel: desenvolvimento e avaliação de um painel web de dados abertos sobre violência e segurança no ambiente escolar a partir da Pesquisa Nacional de Saúde do Escolar*.

## Objetivo

Desenvolver e avaliar um painel web, aberto e reprodutível, que apresente os indicadores de violência e segurança escolar da PeNSE por unidade da federação, capital e perfil do estudante, para apoiar o diagnóstico territorial por gestores educacionais, preservando o rigor estatístico da pesquisa (intervalos de confiança e comparabilidade entre edições).

## Estrutura do repositório

```
Painel-Web-PENSE/
├── config/
│   └── fontes.yaml          # URLs oficiais do IBGE e temas usados
├── data/
│   ├── raw/                 # arquivos originais do IBGE (não versionados)
│   │   └── manifesto.csv    # URL, tamanho e SHA-256 de cada arquivo (versionado)
│   ├── interim/             # tabelas extraídas e padronizadas
│   └── processed/           # base integrada consumida pelo painel
├── src/
│   └── 01_download.py       # etapa 1: download das tabelas oficiais
├── app/                     # código do painel web
├── docs/                    # documentação, dicionário de indicadores
├── tests/                   # testes automatizados
├── requirements.txt
└── README.md
```

O pipeline é numerado (`01_`, `02_`, ...) e cada etapa lê da pasta anterior e grava na seguinte, nunca alterando os arquivos originais em `data/raw/`.

## Fontes dos dados

Tabelas do plano tabular publicadas pelo IBGE:

| Edição | Diretório | Formato |
|---|---|---|
| 2019 | <https://ftp.ibge.gov.br/pense/2019/xls/> | `.xls` |
| 2024 | <https://ftp.ibge.gov.br/pense/2024/xlsx/> | `.xlsx` dentro de `.zip` |

Temas baixados (definidos em `config/fontes.yaml`):

| Chave | Tema do IBGE | Por que entra no painel |
|---|---|---|
| `guia` | Guia de tabelas | Índice que liga cada número de tabela ao indicador |
| `tema_02` | Situações em casa e na escola | Bullying, faltas por insegurança no trajeto ou na escola |
| `tema_09` | Segurança | Brigas, armas, agressão física e violência sexual |
| `tema_17` | Segurança da escola | Questionário respondido pela gestão da escola |

Página oficial da pesquisa: <https://www.ibge.gov.br/estatisticas/sociais/educacao/9134-pense.html>

## Como rodar

Requer **Python 3.10+**.

```bash
# 1. Clonar
git clone https://github.com/caiodantasx/Painel-Web-PENSE.git
cd Painel-Web-PENSE

# 2. Ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Dependências
pip install -r requirements.txt

# 4. Baixar as tabelas do IBGE
python src/01_download.py
```

Opções do `01_download.py`:

```bash
python src/01_download.py --dry-run           # só mostra o que seria baixado
python src/01_download.py --edicoes 2024      # apenas uma edição
python src/01_download.py --temas tema_09     # apenas um tema
python src/01_download.py --force             # baixa de novo, mesmo se já existir
```

### O que o download garante

- **Rastreabilidade:** cada arquivo fica registrado em `data/raw/manifesto.csv` com URL de origem, tamanho, hash SHA-256 e data do download. O manifesto é versionado no Git, então qualquer pessoa consegue verificar se está usando exatamente os mesmos arquivos.
- **Versões corrigidas do IBGE:** o IBGE coloca a data de atualização no nome do arquivo e às vezes republica tabelas corrigidas. O script lê a listagem do diretório e pega a versão mais recente de cada tema; se a listagem estiver fora do ar, usa o nome conferido em `fontes.yaml` (coluna `origem_nome` do manifesto indica qual caso ocorreu).
- **Idempotência:** rodar de novo não baixa o que já existe.
- **Robustez:** novas tentativas automáticas quando o servidor do IBGE oscila, e o arquivo só aparece na pasta quando o download termina por completo.

## Testes

```bash
pytest -q
```

Os testes sobem um servidor local que imita o diretório do IBGE, então rodam sem internet.

## Equipe

Grupo **PeNSE em Painel**.

## Licença dos dados

Os dados são do IBGE, publicados como dados abertos. Ao usar, cite: IBGE. *Pesquisa Nacional de Saúde do Escolar: 2019* e *Pesquisa Nacional de Saúde do Escolar: 2024*. Rio de Janeiro: IBGE.
