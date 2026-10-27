"""Correspondência candidata: perguntas do aluno PeNSE 2015 (seção B9) × tabelas do Tema 9 da PeNSE 2024.

Os textos de 2015 vêm de config/reference/questionario_pense_2015_aluno.csv e os de 2024 do
guia oficial (config/reference/guia_tabelas_pense_2024.csv). A relação e as diferenças abaixo
são a leitura do pesquisador sobre esses textos — **nenhum par é declarado comparável aqui**.
Um par só entra em série histórica quando houver tabela 2015 com o mesmo universo (13 a 17
anos, Amostra 2) e decisão registrada em config/comparability_decisions.csv.

Uso:  python scripts/build_crosswalk.py
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "config" / "reference"

# (variável 2015, família 2024, relação, diferenças observadas nos textos)
PAIRS = [
    ("B09001", "9.7", "MESMO_CONCEITO_CANDIDATO", "Mesmo local (trajeto casa-escola) e mesmo período (30 dias). 2015 mede nº de dias; 2024 publica percentual que não compareceu (≥1 dia, a confirmar)."),
    ("B09002", "9.8", "MESMO_CONCEITO_CANDIDATO", "Mesmo local (na escola) e período (30 dias). Ponto de corte do indicador 2024 a confirmar."),
    ("B09006a1", "9.1", "CONCEITO_PROXIMO_COM_DIFERENCAS", "2024 agrega banco da frente OU de trás e conta 'nunca ou raramente'. 2015 pergunta cada banco separado; quem não andou no veículo é excluído do denominador em 2024 (nota da tabela)."),
    ("B09006a2", "9.1", "CONCEITO_PROXIMO_COM_DIFERENCAS", "Ver B09006a1: 2024 agrega os dois bancos."),
    ("B09006a1", "9.2", "MESMO_CONCEITO_CANDIDATO", "9.2 publica por localização do banco (frente); categorias 'nunca' e 'raramente' existem em 2015."),
    ("B09006a2", "9.2", "MESMO_CONCEITO_CANDIDATO", "9.2 publica por localização do banco (trás)."),
    ("B09007a", "9.3", "CONCEITO_PROXIMO_COM_DIFERENCAS", "Mesmo período e mesmo filtro (quem andou de moto). Quais categorias de 2015 ('sempre', 'na maior parte do tempo'…) formam 'usaram capacete' em 2024 está pendente."),
    ("B09008", "9.4", "MESMO_CONCEITO_CANDIDATO", "Conduziu veículo motorizado nos 30 dias; 2015 cita voadeira e barco como exemplos — conferir se o texto de 2024 é igual."),
    ("B09009", "9.5", "MESMO_CONCEITO_CANDIDATO", "Andou em veículo com condutor que bebeu, 30 dias."),
    ("", "9.6", "SEM_CORRESPONDENTE", "Condutor usando celular: pergunta não existe na seção B9 de 2015."),
    ("B09011", "9.9", "CONCEITO_DIFERENTE", "Período diferente: 2015 pergunta briga com luta física nos 12 meses; 2024 publica 30 dias."),
    ("B09004", "9.10", "MESMO_CONCEITO_CANDIDATO", "Briga com arma de fogo, 30 dias."),
    ("B09005", "9.11", "CONCEITO_PROXIMO_COM_DIFERENCAS", "2015 descreve 'outra arma como faca, canivete, peixeira, pedra, pedaço de pau ou garrafa'; 2024 diz 'arma branca' — pedra, pau e garrafa podem não estar incluídos."),
    ("B09012", "9.12", "CONCEITO_DIFERENTE", "2015: 'seriamente ferido(a)'; 2024: 'sofreram acidente ou agressão'. Eventos e gravidade diferentes."),
    ("B09013a", "9.14", "CONCEITO_PROXIMO_COM_DIFERENCAS", "Tipo da lesão mais séria. Universo difere: 2015 = quem teve ferimento sério; 2024 = quem sofreu acidente ou agressão. Comparar categorias uma a uma."),
    ("B09014a", "9.15", "CONCEITO_PROXIMO_COM_DIFERENCAS", "Causa da lesão mais séria; mesmo problema de universo que 9.14. Lista de causas a conferir categoria a categoria."),
    ("B09003", "9.16", "CONCEITO_DIFERENTE", "Agressor e período diferentes: 2015 'adulto da sua família', 30 dias; 2024 'mãe, pai ou responsável', 12 meses."),
    ("B09010", "9.17", "CONCEITO_DIFERENTE", "2015 pergunta agressão física por qualquer pessoa (12 meses); 2024 exclui mãe, pai ou responsável."),
    ("", "9.13", "SEM_CORRESPONDENTE", "Consequência (deixou atividades / procurou serviço de saúde): sem pergunta equivalente na B9 de 2015."),
    ("", "9.18", "SEM_CORRESPONDENTE", "Identificação do agressor (fora da família): sem pergunta equivalente na B9 de 2015."),
    ("", "9.19", "SEM_CORRESPONDENTE", "Toque/exposição contra a vontade: sem pergunta equivalente no questionário de 2015."),
    ("", "9.20", "SEM_CORRESPONDENTE", "Agressor do toque/exposição: sem pergunta equivalente no questionário de 2015."),
    ("B09016", "9.21", "CONCEITO_PROXIMO_COM_DIFERENCAS", "2015: 'forçado(a) a ter relação sexual'; 2024: 'ameaçou, intimidou ou obrigou a ter relações sexuais ou qualquer outro ato sexual' — conceito de 2024 é mais amplo. Em 2015 a pergunta é pulada para menores de 13 anos na amostra tipo 2."),
    ("B09017", "9.22", "CONCEITO_PROXIMO_COM_DIFERENCAS", "Quem forçou (múltipla resposta nos dois anos?). Categorias 2015: namorado(a), amigo(a), pai/mãe/padrasto/madrasta, outros familiares, desconhecido(a), outro."),
    ("", "9.23", "SEM_CORRESPONDENTE", "Idade em que aconteceu: sem pergunta equivalente em 2015."),
    ("B09015", "", "SEM_CORRESPONDENTE", "Acidente de bicicleta (questão nova em 2015): sem tabela no Tema 9 de 2024."),
]

COMMON = ("Universo: 2024 = escolares de 13 a 17 anos. Em 2015 só a Amostra 2 tem esse universo; as tabelas "
          "2015 já processadas são da Amostra 1 (9º ano) e do questionário da escola — comparação exige tabelas "
          "2015 Amostra 2 do aluno e o questionário 2024 para conferir o texto exato.")


def main() -> None:
    def read(name):
        with (REF / name).open(encoding="utf-8-sig", newline="") as fh:
            return list(csv.DictReader(fh))
    q = {r["variable"]: r for r in read("questionario_pense_2015_aluno.csv")}
    g = {r["table_family_id"]: r for r in read("guia_tabelas_pense_2024.csv")
         if r["theme_id"] == "9" and r["sheet_name"].endswith(".2")}
    out = []
    for var, fam, rel, diff in PAIRS:
        qq, gg = q.get(var, {}), g.get(fam, {})
        if var and not qq:
            raise SystemExit(f"variável {var} não está no questionário extraído")
        if fam and not gg:
            raise SystemExit(f"família {fam} não está no guia")
        out.append({
            "variable_2015": var, "question_2015": qq.get("question_text", ""),
            "period_2015": qq.get("reference_period_code", ""), "change_vs_previous_edition": qq.get("change_vs_previous", ""),
            "table_family_2024": fam, "title_2024": gg.get("title", "").split(", com indicação")[0],
            "relation": rel, "differences": diff, "comparability_status": "PENDING_REVIEW" if rel.startswith(("MESMO", "CONCEITO_PROXIMO")) else ("NOT_COMPARABLE" if rel == "CONCEITO_DIFERENTE" else ""),
            "universe_note": COMMON,
            "review_status": "A_VALIDAR_PELO_PESQUISADOR",
        })
    with (REF / "correspondencia_2015_aluno_x_2024_tema9.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    print(f"{len(out)} linhas de correspondência")


if __name__ == "__main__":
    main()
