"""Grava as decisões APROVADAS pelo pesquisador na matriz de 27/10/2026 (lista de marcação).

Uso (na raiz do projeto): python reports/matriz_comparabilidade_2026-10-27/scripts/registrar_aprovadas.py
Idempotente: reescreve as linhas destes indicadores e preserva as demais.

Marcações do pesquisador (27/10/2026, ~18:30):
  A (7), B (ESCOLA_INSEGURA, 2015 fora), atualizar texto de TRAJETO (classificação mantida), C (8), D (6),
  E (9, série 2015–2019) e retirar 2024 da série do 9º ano. NÃO marcado: ESCOLA_LOCAL_DROGAS (fica sem decisão).
Responsável e data informados pelo pesquisador: Caio Justino De Andrade, 2026-10-27.
Observação do pesquisador: aprovar a comparabilidade NÃO transforma a comparação em validada; ressalvas e
evidências ficam no registro.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MAT = ROOT / "reports/matriz_comparabilidade_2026-10-27"
DEC = ROOT / "config/microdata/comparability_decisions.csv"
EXC = ROOT / "config/microdata/series_exclusions.csv"
REVIEWER, DATE = "Caio Justino De Andrade", "2026-10-27"

APROVADOS = {
    "A": ["CINTO_NUNCA_RARAMENTE", "CINTO_FRENTE", "CINTO_TRAS", "CONDUZIU_VEICULO", "CONDUTOR_ALCOOL",
          "BRIGA_ARMA_FOGO", "BRIGA_ARMA_BRANCA"],
    "B": ["ESCOLA_INSEGURA"],
    "C": ["CONDUTOR_CELULAR", "BRIGA_LUTA_FISICA", "ACIDENTE_OU_AGRESSAO", "TOQUE_SEM_CONSENTIMENTO",
          "RELACAO_SEXUAL_FORCADA", "CAPACETE_QUALQUER_USO", "AGREDIDO_PAIS", "AGREDIDO_OUTROS"],
    "D": ["ESCOLA_LOCAL_ASSALTOS", "ESCOLA_LOCAL_TIROS", "ESCOLA_LOCAL_AGRESSAO", "ESCOLA_LOCAL_ASSASSINATO",
          "ESCOLA_LOCAL_VIOLENCIA_SEXUAL", "ESCOLA_SUSPENDEU_AULAS"],
    "E": ["NONO_CINTO_FRENTE", "NONO_CINTO_TRAS", "NONO_CAPACETE_NUNCA_RARAMENTE", "NONO_CONDUZIU_VEICULO",
          "NONO_CONDUTOR_ALCOOL", "NONO_TRAJETO_INSEGURO", "NONO_ESCOLA_INSEGURA", "NONO_TRAJETO_OU_ESCOLA",
          "NONO_BRIGA_ARMA_BRANCA"],
}
MATRIZ_REF = ("reports/matriz_comparabilidade_2026-10-27/matriz_decisao_36_indicadores.csv (linha do indicador) · "
              "reports/matriz_comparabilidade_2026-10-27/registro_fontes.csv (hash e origem de cada documento)")
SENS_REF = "reports/matriz_comparabilidade_2026-10-27/sensibilidade_6ano_todos.md"


def safe(t: str) -> str:
    """O painel quebra justificativas em itens no '; '. Dentro de () e [] usa ' · ' (e ' a ' em intervalos)."""
    t = re.sub(r"\[([^\]]*?); ([^\]]*?)\]", r"[\1 a \2]", t)

    def par(m):
        return m.group(0).replace("; ", " · ")
    return re.sub(r"\([^()]*\)", par, t)


rows = {r["indicator_key"]: r for r in csv.DictReader((MAT / "matriz_decisao_36_indicadores.csv").open(encoding="utf-8-sig"))}

new_dec, new_exc = {}, []
for bloco, keys in APROVADOS.items():
    for k in keys:
        r = rows[k]
        assert r["status_codigo"] == "COMPARABLE_WITH_CAVEATS", k
        serie = r["edicoes_serie_proposta"].replace("|", ", ")
        just = (f"APROVADA pelo pesquisador na matriz de 27/10/2026 (bloco {bloco}) para a série {serie}. "
                f"A aprovação da comparabilidade NÃO altera o status de validação das estimativas. "
                f"VALIDAÇÃO CONTRA TABELAS OFICIAIS: {r['validacao_tabelas_oficiais']}. "
                f"JUSTIFICATIVA: {r['justificativa']} "
                f"NÃO RESPOSTA: {r['regra_nao_resposta']}. "
                f"LIMITAÇÃO RESIDUAL: {r['limitacao_residual']}. "
                f"RECOMENDAÇÃO: {r['recomendacao']}")
        ev = f"{r['fontes']} · {MATRIZ_REF}" + (f" · {SENS_REF}" if bloco in "AB" else "")
        new_dec[k] = {"indicator_key": k, "final_status": "COMPARABLE_WITH_CAVEATS", "justification": safe(just),
                      "evidence_reference": safe(ev), "reviewer": REVIEWER, "decision_date": DATE}

# --- exclusões aprovadas
s = {r["indicator_key"]: r for r in csv.DictReader((MAT / "sensibilidade_6ano_todos.csv").open(encoding="utf-8"))}["ESCOLA_INSEGURA"]
new_exc.append({"indicator_key": "ESCOLA_INSEGURA", "edition_id": "PENSE_2015_A2", "reason": safe(
    "Exclusão PROVISÓRIA de 2015 (Amostra 2) da série principal de ESCOLA_INSEGURA, pelo mesmo critério já aplicado a "
    "TRAJETO_INSEGURO. Cobertura: a Amostra 2 de 2015 incluiu turmas do 6º ano (IBGE 2022, p. 14, nota 3, e p. 15) e "
    "2019/2024 começam no 7º ano (Manual de Instrução 2019, p. 7 e 12 · PeNSE 2024, Notas técnicas, PDF p. 17). "
    f"Sensibilidade (Brasil, 13 a 17 anos, regra da série · recorte pelo ano autodeclarado): o 6º ano pesa {s['peso_6ano_2015']}% do "
    f"denominador de 2015; 2015 passa de {s['p2015']}% para {s['p2015_sem6']}% sem ele, e a variação 2015→2019 passa de "
    f"{s['d_todos']} p.p. (não significativa a 5%) para {s['d_2015sem6']} p.p. (significativa); retirando também quem se declara no "
    f"6º ano em 2019: {s['d_ambos_sem6']} p.p. (significativa). A conclusão depende do 6º ano: é o MOTIVO da exclusão provisória e "
    "NÃO prova que o valor de 2015 esteja errado. O IBGE recomenda comparar 2024 com 2015 (Amostra 2) para Brasil e Grandes "
    "Regiões em nível de pesquisa (PeNSE 2024, Notas técnicas, Quadro 1), recomendação que não testa este efeito de cobertura. "
    "Valores de 2015 preservados e consultáveis separadamente."),
    "evidence_reference": safe(f"{SENS_REF}, gerado por reports/matriz_comparabilidade_2026-10-27/scripts/sensibilidade_6ano_todos.py · "
                               "IBGE, Estudos e Pesquisas n. 46 (2022), p. 14 nota 3 e p. 15 · data/reference/questionario_pense_2019_aluno.pdf · "
                               "data/reference/liv102266_PeNSE_2024_publicacao.pdf (PDF p. 15 e 17) · " + MATRIZ_REF),
    "reviewer": REVIEWER, "decision_date": DATE})
for k in APROVADOS["E"]:
    new_exc.append({"indicator_key": k, "edition_id": "PENSE_2024", "reason": safe(
        "2024 fora da série principal do 9º ano até haver validação do recorte. A série 2015 (Amostra 1)–2019 é a série oficial "
        "do IBGE (Estudos e Pesquisas n. 46, 2022, tabelas 10.x), validada pelo projeto nas duas edições. O IBGE recomenda "
        "comparar o 9º ano de 2024 com 2015 (A1) e 2019 (PeNSE 2024, Notas técnicas, Quadro 1), mas não publicou tabela do "
        "9º ano para 2024: o valor de 2024 só tem validação INDIRETA (tabelas de 13 a 17 anos). Continua calculado e "
        "consultável em separado, marcado como não validado."),
        "evidence_reference": safe("data/reference/liv101955_PeNSE_indicadores_comparaveis_9ano_2009_2019.pdf · "
                                   "data/reference/liv102266_PeNSE_2024_publicacao.pdf (PDF p. 15, Quadro 1) · "
                                   "data/curated/microdata_validation_summary.csv · " + MATRIZ_REF),
        "reviewer": REVIEWER, "decision_date": DATE})

# --- TRAJETO: só texto (classificação, responsável e data mantidos)
dec_rows = list(csv.DictReader(DEC.open(encoding="utf-8-sig")))
fields = ["indicator_key", "final_status", "justification", "evidence_reference", "reviewer", "decision_date"]
for r in dec_rows:
    if r["indicator_key"] == "TRAJETO_INSEGURO":
        j = r["justification"]
        old2 = "(2) número da questão em 2019 e 2024 pendente (questionários não disponíveis)"
        new2 = ("(2) número da questão: 2019 = q.126 (questionário do aluno 2019, p. 17) · 2024: o questionário identifica o "
                "quesito pelo código B09001 (doc5758, lido na web, não arquivado)")
        old4 = ("(4) turmas de curso técnico integrado e normal/magistério: em 2019 a inclusão está documentada (IBGE 2022, p. 16 · "
                "ANO_TURMA 7 a 12); em 2024 o dicionário não tem códigos próprios para elas e nenhum documento recebido confirma "
                "inclusão ou exclusão: questão NÃO CONFIRMADA")
        new4 = ("(4) turmas de curso técnico integrado e normal/magistério: inclusão documentada nas duas edições (2019: Manual de "
                "Instrução, p. 7 e 12 · IBGE 2022, p. 16 · 2024: PeNSE 2024, Notas técnicas, PDF p. 17): limitação RESOLVIDA em 27/10/2026")
        if old2 in j:
            j = j.replace(old2, new2)
        if old4 in j:
            j = j.replace(old4, new4)
        note = (" ATUALIZAÇÃO DE TEXTO (27/10/2026, aprovada pelo pesquisador, classificação mantida): o IBGE recomenda comparar "
                "2024 com 2019 em todos os níveis e com 2015 (Amostra 2) para Brasil e Grandes Regiões (PeNSE 2024, Notas "
                "técnicas, PDF p. 15, Quadro 1), recomendação em nível de pesquisa que não testa o efeito de cobertura do 6º ano "
                "que motivou a exclusão provisória de 2015.")
        if "ATUALIZAÇÃO DE TEXTO (27/10/2026" not in j:
            j += note
        assert new2 in j and new4 in j, "texto de TRAJETO não encontrado para atualizar"
        r["justification"] = j
        if "liv102266" not in r["evidence_reference"]:
            r["evidence_reference"] += ("; data/reference/questionario_pense_2019_aluno.pdf (q.126, p. 17); "
                                        "data/reference/PeNSE_2019_publicacao.pdf (é o Manual de Instrução 2019: p. 7 e 12); "
                                        "data/reference/liv102266_PeNSE_2024_publicacao.pdf (PDF p. 15 e 17); " + MATRIZ_REF)
keep = [r for r in dec_rows if r["indicator_key"] not in new_dec]
with DEC.open("w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=fields)
    w.writeheader()
    w.writerows(keep + list(new_dec.values()))

exc_rows = list(csv.DictReader(EXC.open(encoding="utf-8-sig")))
efields = ["indicator_key", "edition_id", "reason", "evidence_reference", "reviewer", "decision_date"]
keys_new = {(e["indicator_key"], e["edition_id"]) for e in new_exc}
keep_e = [r for r in exc_rows if (r["indicator_key"], r["edition_id"]) not in keys_new]
with EXC.open("w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=efields)
    w.writeheader()
    w.writerows(keep_e + new_exc)
print(f"decisões: {len(keep) + len(new_dec)} ({len(new_dec)} novas) · exclusões: {len(keep_e) + len(new_exc)} ({len(new_exc)} novas)")
