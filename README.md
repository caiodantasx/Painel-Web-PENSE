# PeNSE em Painel

Painel na internet que mostra dados sobre **violência e segurança nas escolas brasileiras**, usando a **PeNSE** (Pesquisa Nacional de Saúde do Escolar), feita pelo IBGE em **2019** e **2024**.

> TCC: *PeNSE em Painel: desenvolvimento e avaliação de um painel web de dados abertos sobre violência e segurança no ambiente escolar a partir da Pesquisa Nacional de Saúde do Escolar.*

---

## A ideia em uma frase

O IBGE publica os resultados da PeNSE em dezenas de planilhas difíceis de ler. Este projeto **baixa essas planilhas, organiza os números e mostra tudo num painel simples**, para que gestores de educação vejam a situação do seu estado ou capital.

## Como o projeto funciona

O trabalho é dividido em etapas. Cada etapa é um arquivo em `src/`, numerado na ordem em que roda:

```
  Site do IBGE
       │
       ▼
 01_download.py   →  baixa as planilhas oficiais      →  data/raw/
       │
       ▼
 02_...           →  organiza os números (próxima)    →  data/interim/
       │
       ▼
 painel           →  mostra os gráficos               →  app/
```

Hoje existe a **etapa 1**. As outras vêm a seguir.

## O que tem em cada pasta

| Pasta | O que guarda |
|---|---|
| `src/` | Os scripts de cada etapa |
| `data/raw/` | Planilhas originais do IBGE, do jeito que vieram |
| `data/interim/` | Dados já organizados (etapa 2) |
| `data/processed/` | Base final que o painel usa |
| `app/` | O painel |
| `docs/` | Documentação |
| `tests/` | Testes que conferem se os scripts funcionam |

As planilhas não ficam salvas no GitHub, porque qualquer pessoa pode baixá-las de novo rodando o script. Só fica salvo o `data/raw/manifesto.csv`, que é a lista do que foi baixado.

## Quais dados usamos

Da PeNSE, pegamos só os temas sobre violência e segurança:

| Tema | O que tem |
|---|---|
| Tema 02 – Situações em casa e na escola | Bullying, faltar aula por medo |
| Tema 09 – Segurança | Brigas, armas, agressão, violência sexual |
| Tema 17 – Segurança da escola | Respostas da direção da escola |
| Guia de tabelas | Explica o que é cada tabela |

Onde o IBGE publica: <https://ftp.ibge.gov.br/pense/>

## Como rodar no seu computador

**Precisa ter instalado:** [Python](https://www.python.org/downloads/) (marque "Add to PATH" na instalação) e [Git](https://git-scm.com/download/win).

Abra o terminal (no VS Code: menu **Terminal → New Terminal**) e rode um comando por vez:

```bash
# 1. Baixar o projeto
git clone https://github.com/caiodantasx/Painel-Web-PENSE.git
cd Painel-Web-PENSE

# 2. Criar um ambiente separado para o projeto e ativar
python -m venv .venv
.venv\Scripts\activate

# 3. Instalar as bibliotecas
pip install -r requirements.txt

# 4. Baixar os dados do IBGE
python src/01_download.py
```

Se der certo, aparece no final: `Concluído: 8 arquivo(s) ok.`

## Etapa 1 explicada: `01_download.py`

O script faz 4 coisas:

1. **Olha o site do IBGE** para ver quais arquivos existem.
2. **Baixa os temas da tabela acima.** O IBGE coloca a data no nome do arquivo (ex.: `Tema_09_Seguranca_20260615.xls`) e muda essa data quando corrige algo, então o script sempre pega a versão mais nova. Se já tiver baixado antes, ele pula.
3. **Descompacta** os arquivos `.zip` da edição 2024.
4. **Cria o manifesto** (`data/raw/manifesto.csv`): uma lista com o endereço de cada arquivo e um código chamado SHA-256, que funciona como uma impressão digital. Se alguém usar um arquivo diferente, o código muda. Assim dá para provar que os números do painel vêm dos dados oficiais.

Para mudar o que é baixado, basta editar o bloco `FONTES` no começo do script.

## Testes

```bash
pytest -q
```

Os testes criam um "IBGE falso" no próprio computador e conferem se o script baixa os arquivos certos, pega a versão mais nova, descompacta, não baixa duas vezes e continua funcionando quando um arquivo falha. Não precisam de internet.

## Como citar os dados

IBGE. *Pesquisa Nacional de Saúde do Escolar: 2019*. Rio de Janeiro: IBGE.
IBGE. *Pesquisa Nacional de Saúde do Escolar: 2024*. Rio de Janeiro: IBGE.
