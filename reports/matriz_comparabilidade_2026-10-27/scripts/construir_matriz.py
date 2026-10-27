"""Matriz de decisão de comparabilidade dos 36 indicadores (PROPOSTAS — nada é registrado aqui).

Uso: python construir_matriz.py <raiz do projeto> <pasta da matriz>
Lê (sem alterar): config/microdata/indicators.toml, config/reference/dicionario_PENSE_*.csv,
config/reference/questionario_pense_2015_aluno.csv, data/curated/microdata_validation_summary.csv,
data/curated/microdata_comparability.csv; e na pasta da matriz: txt/ (texto extraído dos PDFs),
saida/_loc_dicionarios.json (linha de cada variável nos dicionários originais) e
saida/sensibilidade_6ano_todos.csv.
Escreve: saida/matriz_decisao_36_indicadores.csv e saida/MATRIZ_DECISAO.md.

A redação, os códigos, as validações e a sensibilidade vêm dos arquivos; a classificação proposta, a
justificativa e a limitação residual são texto do analista (bloco PROPOSTAS abaixo), conferido contra as fontes.
"""
from __future__ import annotations

import csv
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
M = Path(sys.argv[2]).resolve()
S = M / "saida" if (M / "saida").is_dir() else M   # pasta de trabalho (saida/) ou cópia no projeto (plana)
OUT_CSV = S / "matriz_decisao_36_indicadores.csv"
OUT_MD = S / "MATRIZ_DECISAO.md"

IND = tomllib.loads((ROOT / "config/microdata/indicators.toml").read_text(encoding="utf-8"))
LOC = json.loads((S / "_loc_dicionarios.json").read_text(encoding="utf-8"))
SENS = {r["indicator_key"]: r for r in csv.DictReader((S / "sensibilidade_6ano_todos.csv").open(encoding="utf-8"))}
VAL = {}
for r in csv.DictReader((ROOT / "data/curated/microdata_validation_summary.csv").open(encoding="utf-8-sig")):
    VAL.setdefault(r["indicator_key"], {})[r["edition_id"]] = r
COMP = {r["indicator_key"]: r for r in csv.DictReader((ROOT / "data/curated/microdata_comparability.csv").open(encoding="utf-8-sig"))}

# ----------------------------------------------------------------------------- dicionários (redação e códigos)
DIC: dict[str, dict[str, tuple[str, str]]] = {}
for ed in ("2015_A2", "2015_A1", "2019", "2024"):
    rows = list(csv.DictReader((ROOT / f"config/reference/dicionario_PENSE_{ed}.csv").open(encoding="utf-8-sig")))
    acc: dict[str, list] = {}
    for r in rows:
        v = re.sub(r"^V(?=B09|E01)", "", r["variable"].strip().upper())
        acc.setdefault(v, [r["description"], []])
        if r["code"] and r["code"] != "nan":
            item = f"{r['code']}={r['code_label']}"
            if item not in acc[v][1]:
                acc[v][1].append(item)
    DIC[ed] = {v: (d, " ; ".join(c)) for v, (d, c) in acc.items()}

Q2015 = {r["variable"].upper(): r for r in csv.DictReader((ROOT / "config/reference/questionario_pense_2015_aluno.csv").open(encoding="utf-8-sig"))}


def page_of(txtfile: str, number: int) -> int | None:
    pages = (M / "txt" / txtfile).read_text(encoding="utf-8").split("\f")
    for i, p in enumerate(pages, 1):
        if re.search(rf"(^|\n)\s*{number}\.\s", p):
            return i
    return None


# número da questão no questionário 2019 (conferido no texto: aluno q.120–143, escola q.56–62)
Q2019 = {"B09006A1": 120, "B09006A2": 121, "B09007A": 122, "B09008": 123, "B09009": 124, "B09019": 125,
         "B09001": 126, "B09002": 127, "B09011A": 128, "B09004": 129, "B09005": 130, "B09012A1": 131,
         "B09003A": 136, "B09010A1": 137, "B09016A1": 139, "B09016A2": 141}
Q2019E = {"E01P79": 56, "E01P80": 57, "E01P81": 58, "E01P82": 59, "E01P83": 60, "E01P84": 61, "E01P59A1": 62}


def loc(ed: str, v: str) -> str:
    x = LOC.get(f"{ed}|{v}")
    return f"aba {x[0]}, linha {x[1]}" if x else "—"


def q2015(v: str) -> str:
    r = Q2015.get(v.upper()) or Q2015.get(v.upper()[:-1] + v[-1].lower()) or Q2015.get(v[:-1].upper() + v[-1].lower())
    for k, rr in Q2015.items():
        if k.upper() == v.upper():
            r = rr
    return f"q.{r['question_number']}, p.{r['page']} (doc4595.pdf)" if r else "—"


def q2019(v: str) -> str:
    if v in Q2019:
        return f"q.{Q2019[v]}, p.{page_of('questionario_aluno_2019.txt', Q2019[v])} (questionário do aluno 2019)"
    if v in Q2019E:
        return f"q.{Q2019E[v]}, p.{page_of('questionario_escola_2019.txt', Q2019E[v])} (questionário da escola 2019)"
    return "—"


def q2024(v: str) -> str:
    if v.startswith("E01"):
        return "PENDENTE: questionário do ambiente escolar 2024 não recebido (redação pelo dicionário 2024)"
    return ("quesito identificado pelo código no questionário do aluno 2024 (doc5758.pdf, bloco B9; lido na web, "
            "arquivo NÃO baixado: sandbox sem acesso ao IBGE). Redação conferida no dicionário 2024")


def vars_of(k: str) -> dict[str, list[str]]:
    d = IND[k]
    if "var_by_edition" in d:
        return {ed: [v] for ed, v in d["var_by_edition"].items()}
    vs = [d["var"]] if "var" in d else [a["var"] for a in d.get("any", [])]
    return {ed: vs for ed in d["editions"]}


def wording(k: str, ed_id: str) -> tuple[str, str, str, str]:
    """(variável, redação, categorias, localização) de uma edição."""
    vs = vars_of(k).get(ed_id)
    if not vs:
        return "—", "—", "—", "—"
    ed = {"PENSE_2015_A2": "2015_A2", "PENSE_2015_A1": "2015_A1", "PENSE_2019": "2019", "PENSE_2024": "2024"}[ed_id]
    out_v, out_t, out_c, out_l = [], [], [], []
    for v in vs:
        d, c = DIC[ed].get(v.upper(), ("NÃO ENCONTRADA NO DICIONÁRIO", ""))
        pref = "V" if ed.startswith("2015") else ""
        out_v.append(pref + v)
        out_t.append(d.rstrip(","))
        out_c.append(c)
        where = loc(ed, v.upper())
        qq = q2015(v) if ed.startswith("2015") else q2019(v.upper()) if ed == "2019" else q2024(v.upper())
        out_l.append(f"dicionário {ed.replace('_', ' ')}: {where}; questionário: {qq}")
    j = " || ".join
    return j(out_v), j(out_t), j(out_c), j(out_l)


def val_text(k: str) -> str:
    out = []
    for ed, r in sorted(VAL.get(k, {}).items()):
        out.append(f"{ed.replace('PENSE_', '')}: {r['status']} — tabela {r['published_table']}"
                   f"{(' · ' + r['published_category']) if r['published_category'] else ''}; "
                   f"{r['reproduz']}/{r['compared']} recortes reproduzem, {r['estimativa_ok_ic_difere']} só IC difere, "
                   f"{r['proximo']} próximos, {r['nao_reproduz']} não reproduzem; diferença máx. {float(r['max_abs_diff_estimate_pp']):.2f} p.p.")
    return " | ".join(out) if out else "sem tabela oficial para validar"


def sens_text(k: str) -> str:
    r = SENS.get(k)
    if not r:
        return "não se aplica (sem 2015 Amostra 2 na proposta)"
    return (f"peso do 6º ano em 2015: {r['peso_6ano_2015']}%; 2015→2019 todos {r['d_todos']} ({'sig.' if r['sig_todos'] == 'True' else 'n.s.'}); "
            f"2015 sem 6º ano {r['d_2015sem6']} ({'sig.' if r['sig_2015sem6'] == 'True' else 'n.s.'}); "
            f"ambos sem 6º {r['d_ambos_sem6']} ({'sig.' if r['sig_ambos_sem6'] == 'True' else 'n.s.'}); "
            f"conclusão {'ROBUSTA' if r['conclusao_2015_2019_robusta'] == 'True' else 'NÃO ROBUSTA'}")


# ----------------------------------------------------------------------------- fontes citadas (chaves → texto)
F = {
    "DIC": "dicionários de microdados do IBGE 2015 (Amostras 1 e 2), 2019 e 2024 (data/reference/dicionarios/; linhas indicadas)",
    "Q15": "Questionário do aluno PeNSE 2015 (doc4595.pdf), bloco B9, p.15–17",
    "Q19": "Questionário do aluno PeNSE 2019 (questionario-aluno-PeNSE-2019.pdf), bloco Segurança, q.120–143, p.16–18",
    "Q19E": "Questionário do ambiente escolar PeNSE 2019 (questionario-escola-PeNSE-2019.pdf), q.56–62, p.6–7",
    "Q24": "Questionário do aluno PeNSE 2024 (biblioteca.ibge.gov.br/visualizacao/instrumentos_de_coleta/doc5758.pdf), bloco B9 — lido na web em 27/10/2026, não arquivado",
    "MAN19": "Manual de Instrução PeNSE 2019 (IBGE, mar. 2019), p.7 e p.12–13: turmas do 7º ano à 3ª série do EM, incluídos técnico integrado e normal/magistério",
    "N24": "PeNSE 2024 (IBGE, liv102266.pdf), Notas técnicas: PDF p.15 (impressa 12), Quadro 1, 'Comparabilidade recomendada com edições anteriores'; PDF p.17 (impr. 14): 7º ano à 3ª série, incluídos técnico integrado e normal/magistério, mesma população-alvo de 2019; PDF p.25 (impr. 22): códigos distintos para salto, abandono e não resposta",
    "T6": "PeNSE 2024 (liv102266.pdf), PDF p.131 (impressa 128), Tabela 6: comparação 2019/2024 do IBGE para cinto (3), capacete, conduziu, álcool e celular",
    "TXT24": "PeNSE 2024 (liv102266.pdf), capítulo Segurança e violências, PDF p.127–143 (impressas 124–140)",
    "E46": "IBGE, Estudos e Pesquisas n. 46 (2022), Análise de indicadores comparáveis do 9º ano 2009/2019 (liv101955.pdf): p.14 nota 3 e p.15 (cobertura 2015 A2), p.18 nota 7 (sem resposta × abandono), série oficial 10.x; PDF p.133 (impr. 131) e nota 42 (mudanças em briga com luta física)",
    "NM03": "Nota metodológica n. 03 (IBGE, 2018), especificação das tabelas da Amostra 2 de 2015 (2.11.x)",
    "NT01": "Nota técnica 01/2022 (controle de confidencialidade dos microdados de 2019)",
    "VAL": "data/curated/microdata_validation_summary.csv (reprodução das tabelas oficiais pelo projeto)",
    "SENS": "reports/matriz_comparabilidade_2026-10-27/sensibilidade_6ano_todos.md (gerado por reports/matriz_comparabilidade_2026-10-27/scripts/sensibilidade_6ano_todos.py)",
}

COMUM_19_24 = ("2019 e 2024: mesma variável, mesma redação e mesmas categorias nos dicionários; mesmo informante; "
               "mesma cobertura documentada (7º ano à 3ª série do EM, com técnico integrado e normal/magistério: MAN19 p.7/12; "
               "N24 PDF p.17) e mesma população-alvo (13 a 17 anos; N24 PDF p.17); IBGE recomenda comparar 2024 com 2019 "
               "em todos os níveis geográficos (N24, Quadro 1)")
NR_19_24 = ("2019: 9 = sem resposta (entra no denominador), -2 = abandono (fora); 2024: -9 = sem resposta (entra), "
            "-2 = abandono (fora). Regra CONFIRMADA por reprodução das tabelas oficiais; nenhum documento recebido "
            "a especifica para essas tabelas (N24 PDF p.25 só informa que os códigos existem) — LACUNA DOCUMENTAL")
NR_15 = ("2015: 99 = 'não informado' (mistura sem resposta e abandono) fora do denominador na publicação (NM03); "
         "na série harmonizada o abandono é reconstruído (99 sem nenhuma resposta posterior) e o sem resposta entra "
         "(E46 p.18 nota 7)")
LIM_19_24 = ("regra de não resposta 2019/2024 sustentada por reprodução (lacuna documental); microdados 2019 com controle "
             "de confidencialidade (NT01), daí VALIDADO_COM_RESSALVA em 2019; desenhos amostrais próprios de cada edição; "
             "comparabilidade não equivale a mudança significativa")

# ----------------------------------------------------------------------------- PROPOSTAS (texto do analista)
# bloco: rótulo da lista de aprovação; status: COMPARABLE / COMPARABLE_WITH_CAVEATS / NOT_COMPARABLE / PENDING_REVIEW
P: dict[str, dict] = {}


def prop(keys, **kw):
    for k in keys:
        P[k] = dict(kw)


A = ["CINTO_NUNCA_RARAMENTE", "CINTO_FRENTE", "CINTO_TRAS", "CONDUZIU_VEICULO", "CONDUTOR_ALCOOL", "BRIGA_ARMA_FOGO", "BRIGA_ARMA_BRANCA"]
prop(A, bloco="A", status="COMPARABLE_WITH_CAVEATS", serie="PENSE_2015_A2|PENSE_2019|PENSE_2024",
     fontes="DIC; Q15; Q19; Q24; MAN19; N24; E46; NM03; VAL; SENS",
     justificativa=("Mesma variável e mesma pergunta em 2015, 2019 e 2024 (dicionários e questionários); mesmo período "
                    "(30 dias) e mesmos códigos de numerador e denominador; cálculo reproduz as tabelas oficiais nas três "
                    "edições; IBGE recomenda comparar 2024 com 2015 (Amostra 2) para Brasil e Grandes Regiões (N24, "
                    "Quadro 1); a conclusão 2015→2019 não muda sem o 6º ano (sensibilidade robusta). " + COMUM_19_24),
     limitacao=("2015 só para Brasil e Grandes Regiões; Amostra 2 de 2015 inclui o 6º ano (E46 p.14–15) — "
                "sensibilidade robusta, mas o recorte por ano autodeclarado é aproximação; posição no questionário "
                "mudou (2015: q.03–10 logo após as faltas por insegurança; 2019/2024: bloco de trânsito antes das "
                "faltas), efeito de contexto não testável; " + LIM_19_24),
     recomendacao="USAR na série histórica 2015–2019–2024 (2015 só Brasil e Grandes Regiões), com as ressalvas.")
P["CINTO_NUNCA_RARAMENTE"]["extra"] = P["CINTO_FRENTE"]["extra"] = P["CINTO_TRAS"]["extra"] = (
    "Rótulos de duas categorias mudaram de 2015 para 2019 sem mudar o código: 1 'Não andei nesse tipo de veículo no "
    "banco da frente/de trás' → 'Não andei no banco da frente/de trás' e 5 'Na maior parte do tempo' → 'Na maioria das "
    "vezes'. O código 1 sai do denominador nas três edições; o 5 fica no denominador e fora do numerador. IBGE "
    "compara 2019 e 2024 (T6). Mudança de redação considerada NÃO substantiva, mas registrada.")
P["CONDUZIU_VEICULO"]["extra"] = ("2015 'motocicleta' → 2019/2024 'motocicleta/moto' no exemplo da pergunta (não substantivo). "
                                  "IBGE compara 2019 e 2024 (T6). 2024 VALIDADO_COM_RESSALVA (17 recortes não idênticos, máx. 0,23 p.p.).")
P["CONDUTOR_ALCOOL"]["extra"] = "Redação idêntica nas três edições. IBGE compara 2019 e 2024 (T6)."
P["BRIGA_ARMA_FOGO"]["extra"] = ("Redação idêntica nas três edições. Queda grande de 2015 (6,3%) para 2019 (2,9%) com a mesma "
                                 "pergunta: em 2015 ela vinha logo após 'agredido por um adulto da família' (q.08); em 2019 "
                                 "e 2024, após 'briga com luta física' (q.128) — possível efeito de contexto, não testável. "
                                 "IBGE não comenta a comparação no texto de 2024.")
P["BRIGA_ARMA_BRANCA"]["extra"] = ("Redação idêntica nas três edições; mesma observação de contexto que BRIGA_ARMA_FOGO. IBGE não "
                                   "comenta a comparação no texto de 2024 (a série oficial do 9º ano 2009–2019 usa a mesma pergunta: E46 PDF p.133).")
P["CINTO_NUNCA_RARAMENTE"]["extra"] += " Validado também em 2015 contra a tabela 2.11.3 (frente ou trás)."

prop(["ESCOLA_INSEGURA"], bloco="B", status="COMPARABLE_WITH_CAVEATS", serie="PENSE_2019|PENSE_2024", excluir="PENSE_2015_A2",
     fontes="DIC; Q15; Q19; Q24; MAN19; N24; TXT24; E46; VAL; SENS",
     justificativa=("2019–2024: " + COMUM_19_24 + "; o próprio IBGE compara as duas edições (+2,9 p.p. em relação a 2019; "
                    "TXT24, PDF p.132). 2015: mesma pergunta, mas a conclusão 2015→2019 MUDA sem o 6º ano "
                    "(+0,70 n.s. → +1,38 sig.), o mesmo critério que retirou 2015 de TRAJETO_INSEGURO. Proposta coerente "
                    "com aquela decisão: 2015 fora da série principal, preservado para consulta."),
     limitacao=("exclusão de 2015 provisória (a sensibilidade é o motivo, não prova de erro; IBGE recomenda a comparação "
                "com 2015 em nível de pesquisa — N24, Quadro 1); " + LIM_19_24),
     recomendacao="USAR 2019–2024 na série; 2015 fora da série principal (consulta separada), como em TRAJETO_INSEGURO.",
     extra="Em 2015 a pergunta era a q.02 (abertura do bloco); em 2019 e 2024 vem após o bloco de trânsito (q.127).")

C = ["CONDUTOR_CELULAR", "BRIGA_LUTA_FISICA", "ACIDENTE_OU_AGRESSAO", "TOQUE_SEM_CONSENTIMENTO", "RELACAO_SEXUAL_FORCADA",
     "CAPACETE_QUALQUER_USO", "AGREDIDO_PAIS", "AGREDIDO_OUTROS"]
prop(C, bloco="C", status="COMPARABLE_WITH_CAVEATS", serie="PENSE_2019|PENSE_2024",
     fontes="DIC; Q19; Q24; MAN19; N24; VAL",
     justificativa=COMUM_19_24 + "; cálculo reproduz as tabelas oficiais de 2019 e 2024.",
     limitacao=LIM_19_24,
     recomendacao="USAR na série 2019–2024, com as ressalvas.")
P["CONDUTOR_CELULAR"]["extra"] = "Pergunta nova em 2019 (E46 PDF p.129). IBGE compara 2019 e 2024 (T6). Sem 2015."
P["CONDUTOR_CELULAR"]["fontes"] += "; T6; E46"
P["BRIGA_LUTA_FISICA"]["extra"] = ("2015 NÃO comparável: VB09011 'NOS ÚLTIMOS 12 MESES, quantas vezes você se envolveu em briga "
                                    "(uma luta física)?' (período e escala diferentes; E46 PDF p.133 confirma a mudança). IBGE "
                                    "compara 2019 e 2024 (+0,6 p.p.; TXT24 PDF p.135).")
P["BRIGA_LUTA_FISICA"]["fontes"] += "; TXT24; E46; Q15"
P["ACIDENTE_OU_AGRESSAO"]["extra"] = ("2015 NÃO comparável: VB09012 'quantas vezes você foi seriamente ferido(a)?' (outro conceito). "
                                       "IBGE compara 2019 e 2024 (−0,9 p.p.; TXT24 PDF p.136).")
P["ACIDENTE_OU_AGRESSAO"]["fontes"] += "; TXT24; Q15"
P["TOQUE_SEM_CONSENTIMENTO"]["extra"] = ("Pergunta nova em 2019. Em 2019 e 2024 só aparece para quem tem 13 anos ou mais (Q19 p.18; "
                                          "N24 PDF p.17). IBGE compara 2019 e 2024 (+3,8 p.p.; TXT24 PDF p.141).")
P["TOQUE_SEM_CONSENTIMENTO"]["fontes"] += "; TXT24"
P["RELACAO_SEXUAL_FORCADA"]["extra"] = ("2015 NÃO comparável: VB09016 'Alguma vez na vida você foi forçado a ter relação sexual?' — "
                                         "2019/2024 ampliam para 'ameaçou, intimidou ou obrigou a ter relações sexuais ou qualquer "
                                         "outro ato sexual' (mudança substantiva). Filtro de 13+ anos em 2019 e 2024. IBGE compara "
                                         "2019 e 2024 (+2,5 p.p.; TXT24 PDF p.142).")
P["RELACAO_SEXUAL_FORCADA"]["fontes"] += "; TXT24; Q15"
P["CAPACETE_QUALQUER_USO"]["extra"] = ("Definição das tabelas 9.3 de 2019 e 2024 (raramente a sempre). 2015 fica fora: a tabela "
                                        "2015 (2.11.5) publicou outra definição (às vezes a sempre), então o ponto de 2015 nesta "
                                        "definição não tem tabela oficial para validar; rótulos 'motocicleta' → 'motocicleta/moto' "
                                        "e 'Na maior parte do tempo' → 'Na maioria das vezes'. IBGE compara 2019 e 2024 e diz que "
                                        "'não houve mudança significativa' (TXT24 PDF p.130; T6).")
P["CAPACETE_QUALQUER_USO"]["fontes"] += "; T6; TXT24; NM03"
P["AGREDIDO_PAIS"]["extra"] = ("2015 NÃO comparável: VB09003 '30 dias', 'por um adulto da sua família', escala até 12+ vezes. "
                                "IBGE apresenta 2024 sem comparar com 2019 no texto (TXT24 PDF p.139–140); comparabilidade "
                                "proposta pela evidência documental, não por declaração do IBGE.")
P["AGREDIDO_PAIS"]["fontes"] += "; Q15; TXT24"
P["AGREDIDO_OUTROS"]["extra"] = ("2015 NÃO comparável: VB09010 'quantas vezes você foi agredido(a) fisicamente?' sem distinguir "
                                  "o agressor. IBGE não compara com 2019 no texto (TXT24 PDF p.140); comparabilidade pela "
                                  "evidência documental.")
P["AGREDIDO_OUTROS"]["fontes"] += "; Q15; TXT24"

E = ["ESCOLA_LOCAL_ASSALTOS", "ESCOLA_LOCAL_TIROS", "ESCOLA_LOCAL_AGRESSAO", "ESCOLA_LOCAL_ASSASSINATO",
     "ESCOLA_LOCAL_VIOLENCIA_SEXUAL", "ESCOLA_SUSPENDEU_AULAS"]
prop(E, bloco="D", status="COMPARABLE_WITH_CAVEATS", serie="PENSE_2019|PENSE_2024",
     fontes="DIC; Q19E; N24; TXT24; VAL",
     justificativa=("Questionário do ambiente escolar: mesma variável, mesma redação e mesmas categorias em 2019 (q.56–62) "
                    "e 2024 (dicionários); mesmo informante (diretor ou responsável); indicador expresso em % de escolares "
                    "de 13 a 17 anos em escolas com a situação (N24 PDF p.14; TXT24 PDF p.133–134); reproduz as tabelas "
                    "17.1/17.2 de 2019 e 2024."),
     limitacao=("percepção do diretor ('presenciou ou ouviu falar'), não ocorrência; informante pode mudar de pessoa entre "
                "edições; resultados representam as escolas frequentadas pelos escolares da amostra, não o total de escolas "
                "(N24 PDF p.14); IBGE não compara 2019 e 2024 no texto; número da questão em 2024 pendente (questionário da "
                "escola 2024 não recebido); sem resposta: 9 (2019) e -9 (2024), regra por reprodução; "
                "2019 VALIDADO_COM_RESSALVA (menos recortes, 73)"),
     recomendacao="USAR na série 2019–2024, com as ressalvas.")
P["ESCOLA_SUSPENDEU_AULAS"]["extra"] = "Pergunta filtro (q.62 em 2019); a q.63 (quantas vezes) não é usada."

prop(["ESCOLA_LOCAL_DROGAS"], bloco="D-NC", status="NOT_COMPARABLE", serie="",
     fontes="DIC; Q19E; TXT24; VAL",
     justificativa=("Mudança substantiva de redação: 2019 (E01P81, q.58) 'havia alguém vendendo drogas'; 2024 (E01P81A) "
                    "'havia alguém vendendo ou usando drogas'. O sufixo novo e o texto ampliam o conceito em 2024. "
                    "Cada edição reproduz a própria tabela 17.1, mas medem coisas diferentes."),
     limitacao="o publicado de cada edição continua válido isoladamente; a diferença entre os anos não deve ser interpretada",
     recomendacao="NÃO USAR na série histórica; mostrar 2019 e 2024 separados, com nota.")

N9 = ["NONO_CINTO_FRENTE", "NONO_CINTO_TRAS", "NONO_CAPACETE_NUNCA_RARAMENTE", "NONO_CONDUZIU_VEICULO", "NONO_CONDUTOR_ALCOOL",
      "NONO_TRAJETO_INSEGURO", "NONO_ESCOLA_INSEGURA", "NONO_TRAJETO_OU_ESCOLA", "NONO_BRIGA_ARMA_BRANCA"]
prop(N9, bloco="E", status="COMPARABLE_WITH_CAVEATS", serie="PENSE_2015_A1|PENSE_2019", excluir="PENSE_2024",
     fontes="DIC; Q15; Q19; E46; N24; VAL",
     justificativa=("2015 (Amostra 1) e 2019: indicador da série oficial do IBGE para o 9º ano 2009–2019 (E46, tabelas 10.x), "
                    "com regra de não resposta documentada (E46 p.18 nota 7); mesma variável e redação; o cálculo reproduz "
                    "a tabela da série nas duas edições. 2024: o IBGE recomenda a comparação do 9º ano com 2015 (A1) e 2019 "
                    "(N24, Quadro 1), mas não publicou tabela do 9º ano para 2024 — o ponto de 2024 não tem validação oficial."),
     limitacao=("a série oficial E46 é dos Municípios das Capitais (é contra ela que o projeto valida, 140 recortes); "
                "o IBGE também recomenda Brasil/GR 2015 A1–2019 (N24, Quadro 1), mas sem tabela da série para validar esses níveis; "
                "2024 sem tabela oficial do 9º ano (validação INDIRETA, pelas tabelas 13–17); microdados 2019 com controle "
                "de confidencialidade (NT01)"),
     recomendacao=("USAR 2015–2019 (série oficial do IBGE). 2024 fica PENDENTE fora da série principal até haver validação "
                   "do recorte do 9º ano (pode ser exibido em separado, marcado como não validado)."))
P["NONO_BRIGA_ARMA_BRANCA"]["extra"] = "Série oficial 10.11; 2015 A1 e 2019 VALIDADO."
P["NONO_CAPACETE_NUNCA_RARAMENTE"]["extra"] = ("2019 VALIDADO_COM_RESSALVA com diferença máxima de 1,72 p.p. em recorte pequeno; "
                                                "rótulos 'motocicleta' → 'motocicleta/moto' e 'Na maior parte do tempo' → 'Na maioria das vezes'.")
P["NONO_CINTO_FRENTE"]["extra"] = P["NONO_CINTO_TRAS"]["extra"] = (
    "Rótulos das categorias 1 e 5 mudaram de 2015 para 2019 (ver CINTO_FRENTE); IBGE compara 2015 e 2019 na série do 9º ano (E46 PDF p.121).")
P["NONO_TRAJETO_INSEGURO"]["extra"] = "IBGE comenta 2015 (12,8%) → 2019 (12,3%) nas capitais (E46 PDF p.129). Não há o problema do 6º ano (só 9º ano)."

prop(["NONO_BRIGA_LUTA_FISICA"], bloco="F", status="PENDING_REVIEW", serie="",
     fontes="E46; DIC; Q19; Q24; VAL",
     justificativa=("2015 (A1) NÃO comparável: 12 meses e frequência (E46 PDF p.133, nota 42). Restam 2019 (validado, tabela "
                    "10.10) e 2024 (sem tabela oficial do 9º ano). Uma série com um único ponto validado não sustenta "
                    "comparação."),
     limitacao="só 2019 validado", recomendacao="MANTER PENDENTE e fora da série até validar 2024.")
prop(["NONO_CINTO_FRENTE_OU_TRAS"], bloco="F", status="PENDING_REVIEW", serie="",
     fontes="E46; VAL",
     justificativa=("O cálculo do projeto NÃO reproduz a tabela 10.3 da série oficial (2015: 1/140 recortes, diferença até "
                    "2,40 p.p.; 2019: 1/140, até 5,54 p.p.). A falha é da reprodução, não da pergunta: falta descobrir a "
                    "regra de combinação (frente E/OU trás) e de denominador usada pelo IBGE."),
     limitacao="problema de cálculo aberto (pendência 10.3)", recomendacao="MANTER PENDENTE e fora da série.")
prop(["CAPACETE_AS_VEZES_OU_MAIS"], bloco="F", status="PENDING_REVIEW", serie="",
     fontes="NM03; VAL",
     justificativa=("Definição publicada só em 2015 (tabela 2.11.5); 2019 e 2024 não têm tabela com esta definição. A série "
                    "de capacete do painel é CAPACETE_QUALQUER_USO (2019–2024)."),
     limitacao="sem validação oficial em 2019 e 2024", recomendacao="MANTER PENDENTE e fora da série (já está).")

P["TRAJETO_INSEGURO"] = dict(bloco="—", status="COMPARABLE_WITH_CAVEATS", serie="PENSE_2019|PENSE_2024", excluir="PENSE_2015_A2",
    fontes="ver config/microdata/comparability_decisions.csv e series_exclusions.csv; novas: MAN19; N24; Q19; SENS",
    justificativa="DECISÃO JÁ REGISTRADA (Caio Justino De Andrade, 2026-10-27). Nada muda aqui.",
    limitacao=("NOVAS EVIDÊNCIAS para o texto da decisão (não mudam a classificação): (a) técnico integrado e "
               "normal/magistério documentados em 2019 (MAN19 p.7/12) e 2024 (N24 PDF p.17) — fecha a limitação (4); "
               "(b) número da questão 2019 = q.126 (p.17) — fecha parte da limitação (2); (c) IBGE recomenda comparar "
               "2024 com 2015 A2 para Brasil/GR (N24, Quadro 1), em nível de pesquisa — pondera a exclusão provisória de 2015, "
               "que continua sustentada pela sensibilidade."),
    recomendacao="MANTER a decisão registrada; atualizar o texto com (a) e (b) e citar (c), se aprovado.")

assert set(P) == set(IND), sorted(set(IND) ^ set(P))

# ----------------------------------------------------------------------------- linhas
LABEL = {"COMPARABLE": "comparável", "COMPARABLE_WITH_CAVEATS": "comparável com ressalvas",
         "NOT_COMPARABLE": "não comparável", "PENDING_REVIEW": "pendente de validação"}
BLOCO = {"A": "A — 13–17 anos, 2015–2019–2024 (7)", "B": "B — ESCOLA_INSEGURA 2019–2024, 2015 fora (1)",
         "C": "C — aluno 13–17 anos, 2019–2024 (8)", "D": "D — escola (diretor), 2019–2024 (6)",
         "D-NC": "D-NC — ESCOLA_LOCAL_DROGAS não comparável (1)", "E": "E — 9º ano, série 2015–2019; 2024 pendente (9)",
         "F": "F — continuam pendentes (3)", "—": "já registrada"}
rows = []
for k, d in IND.items():
    p = P[k]
    pop = "9º ano do EF" if k.startswith("NONO_") else "escolares de 13 a 17 anos"
    if d.get("informant", "").startswith("Escola"):
        pop += " em escolas cujo diretor/responsável informou a situação (informante: diretor ou responsável)"
    eds15 = "PENSE_2015_A1" if "PENSE_2015_A1" in d["editions"] else "PENSE_2015_A2"
    v15, t15, c15, l15 = wording(k, eds15)
    v19, t19, c19, l19 = wording(k, "PENSE_2019")
    v24, t24, c24, l24 = wording(k, "PENSE_2024")
    num = d.get("num") or "; ".join(f"{a['var']}: {a['num']}" for a in d.get("any", []))
    den = d.get("den") or "; ".join(f"{a['var']}: {a['den']}" for a in d.get("any", []))
    comp = COMP.get(k, {})
    rows.append({
        "indicator_key": k, "rotulo": d["label"], "bloco_aprovacao": BLOCO[p["bloco"]],
        "populacao": pop, "periodo_referencia": {"30_DIAS": "últimos 30 dias", "12_MESES": "últimos 12 meses", "VIDA": "alguma vez na vida"}[d["period"]],
        "edicoes_calculadas": "|".join(d["editions"]),
        "var_2015": v15, "redacao_2015": t15, "categorias_2015": c15, "local_2015": l15,
        "var_2019": v19, "redacao_2019": t19, "categorias_2019": c19, "local_2019": l19,
        "var_2024": v24, "redacao_2024": t24, "categorias_2024": c24, "local_2024": l24,
        "numerador_codigos": str(num), "denominador_codigos": str(den),
        "regra_nao_resposta": (NR_15 + " | " if "2015" in "|".join(d["editions"]) else "") + NR_19_24,
        "validacao_tabelas_oficiais": val_text(k),
        "sensibilidade_6ano_2015": sens_text(k) if "PENSE_2015_A2" in d["editions"] else "não se aplica",
        "status_atual_pipeline": f"{comp.get('final_status', '')} ({comp.get('decision_status', '')})",
        "classificacao_proposta": LABEL[p["status"]], "status_codigo": p["status"],
        "edicoes_serie_proposta": p.get("serie", "").replace("PENSE_", "").replace("_", " "),
        "edicao_fora_da_serie_proposta": p.get("excluir", "").replace("PENSE_", "").replace("_", " "),
        "justificativa": p["justificativa"].rstrip(".") + "." + ((" " + p["extra"]) if p.get("extra") else ""),
        "fontes": "; ".join(F[x.strip()] if x.strip() in F else x.strip() for x in p["fontes"].split(";")),
        "limitacao_residual": p["limitacao"], "recomendacao": p["recomendacao"],
        "registro": "JÁ REGISTRADA" if k == "TRAJETO_INSEGURO" else "NÃO REGISTRADA — aguarda marcação do pesquisador",
    })

with OUT_CSV.open("w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)

# ----------------------------------------------------------------------------- markdown
from collections import Counter  # noqa: E402
cnt = Counter(r["classificacao_proposta"] for r in rows)
md = ["# Matriz de decisão de comparabilidade — 36 indicadores (PROPOSTAS)", "",
      "**Nada aqui está registrado.** Só TRAJETO_INSEGURO tem decisão registrada (27/10/2026). As demais linhas são "
      "propostas para marcação do pesquisador; a pipeline só muda depois do registro.", "",
      "Classificação proposta: " + ", ".join(f"{v} {k}" for k, v in cnt.most_common()) + ".", "",
      "| # | Indicador | Bloco | Edições calculadas | Proposta | Série proposta | Fora da série | Validação (resumo) |",
      "|---|---|---|---|---|---|---|---|"]
for i, r in enumerate(rows, 1):
    vs = re.sub(r" — tabela.*?; ", " ", r["validacao_tabelas_oficiais"])
    vs = "; ".join(x.split(":")[0] + ": " + x.split(":")[1].split(" ")[1] for x in r["validacao_tabelas_oficiais"].split(" | ")) if ":" in r["validacao_tabelas_oficiais"] else r["validacao_tabelas_oficiais"]
    md.append(f"| {i} | `{r['indicator_key']}` | {r['bloco_aprovacao'].split(' —')[0]} | {r['edicoes_calculadas'].replace('PENSE_', '').replace('|', ', ')} | "
              f"**{r['classificacao_proposta']}** | {r['edicoes_serie_proposta'].replace('|', ', ') or '—'} | {r['edicao_fora_da_serie_proposta'] or '—'} | {vs} |")
md += ["", "## Fontes", ""] + [f"* **{k}** — {v}" for k, v in F.items()]
md += ["", "## Detalhe por indicador", ""]
for r in rows:
    md += [f"### {r['indicator_key']} — {r['rotulo']}", "",
           f"* **Proposta:** {r['classificacao_proposta']} · série: {r['edicoes_serie_proposta'].replace('|', ', ') or '—'} · fora: {r['edicao_fora_da_serie_proposta'] or '—'} · bloco {r['bloco_aprovacao']}",
           f"* **População / período:** {r['populacao']} · {r['periodo_referencia']}",
           f"* **2015** `{r['var_2015']}`: {r['redacao_2015']} — {r['local_2015']}",
           f"* **2019** `{r['var_2019']}`: {r['redacao_2019']} — {r['local_2019']}",
           f"* **2024** `{r['var_2024']}`: {r['redacao_2024']} — {r['local_2024']}",
           f"* **Categorias 2019:** {r['categorias_2019']}",
           f"* **Numerador / denominador (códigos):** {r['numerador_codigos']} / {r['denominador_codigos']}",
           f"* **Não resposta:** {r['regra_nao_resposta']}",
           f"* **Validação:** {r['validacao_tabelas_oficiais']}",
           f"* **Sensibilidade ao 6º ano:** {r['sensibilidade_6ano_2015']}",
           f"* **Justificativa:** {r['justificativa']}",
           f"* **Limitação residual:** {r['limitacao_residual']}",
           f"* **Recomendação:** {r['recomendacao']}",
           f"* **Registro:** {r['registro']}", ""]
OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
print(OUT_CSV, len(rows), dict(cnt))
