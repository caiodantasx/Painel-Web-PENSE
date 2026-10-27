# Guia: adicionar novas tabelas, temas ou edições

## Caso 1 — nova tabela de uma família já conhecida (ex.: outro tema da PeNSE 2024)

1. Copie o `.xlsx` ou o `.zip` para `data/raw/`.
2. Rode `python scripts/run_pipeline.py`.
3. Confira em `data/processed/inventory_sheets.csv` se as abas receberam
   `adapter_family = PENSE_2024_IC/CV` e em `data/processed/unparsed_report.csv` se nada
   ficou sem interpretação.
4. Se aparecer `STB001` (seção desconhecida) ou `HDR001` (coluna não interpretada),
   acrescente o rótulo em `config/vocabulary.toml` (ex.: uma nova dimensão como "Cor ou
   raça") e rode de novo.
5. Opcional: rótulo curto do indicador em `config/indicator_labels.csv`.
6. Rode `python -m pytest` e, se o indicador for importante para o TCC, acrescente um teste
   de regressão em `tests/test_adapters_regression.py` com um valor conferido na planilha.

Nenhuma alteração de código é necessária neste caso.

## Caso 2 — nova dimensão (ex.: "Cor ou raça")

Em `config/vocabulary.toml`:

```toml
[dimensions.race]
label = "Cor ou raça"
containers = ["cor ou raca"]
[dimensions.race.values]
branca = "Branca"
preta = "Preta"
parda = "Parda"
```

Depois, inclua a dimensão em `DIMS` (`validation/rules.py`), no dicionário `dims` de
`adapters/base.py::_record` e no esquema (`standardization/schema.py`). O painel lê as
dimensões do pacote de dados.

## Caso 3 — nova edição com estrutura diferente (nova família)

1. Inspecione as planilhas: título, cabeçalho, seções, rodapé, símbolos.
2. Em `src/pense/adapters/families.py`, crie uma classe derivada de `BaseAdapter`:

```python
class Pense2019Adapter(BaseAdapter):
    family_id = "PENSE_2019"
    description = "PeNSE 2019 — tabelas de estimativa com IC95%"

    def detect(self, ctx):
        t, ev, score = ctx.title, [], 0.0
        if t.year == 2019 or t.footer_year == 2019:
            score += 0.4; ev.append("ano 2019 no título/rodapé")
        if t.confidence_level == 95:
            score += 0.3; ev.append("IC 95% no título")
        if re.match(r"^\d+\.\d+\.\d+$", t.table_id):
            score += 0.3; ev.append("código em 3 níveis")
        return Detection(score, ev)

    def edition_id(self, ctx):
        return "PENSE_2019"
```

3. Registre-a em `ALL_ADAPTERS` e acrescente a edição em `config/editions.csv`.
4. Se a família tiver regra própria (outra forma de código de tabela, por exemplo),
   sobrescreva `table_codes`.
5. Escreva testes de regressão com 3 a 5 valores conferidos à mão (célula de origem
   anotada no teste).
6. Rode a pipeline e verifique o relatório de qualidade.

## Caso 4 — correspondência entre edições

1. Acrescente o par em `config/comparability_candidates.csv` (conceito, unidade,
   indicador/categoria de cada lado, motivo).
2. Rode a pipeline e leia `reports/relatorio_comparabilidade.md`.
3. Se a regra automática apontar `PENDING_REVIEW`, consulte questionários e notas
   técnicas; registre a decisão em `config/comparability_decisions.csv` **com
   justificativa e referência**. Veja `06_guia_serie_historica.md`.
