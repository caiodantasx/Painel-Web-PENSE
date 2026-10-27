"""Estimação de proporções em amostras complexas (estratificada, por conglomerados).

Estimador de razão  p = Σ w·y / Σ w·x  num domínio d, com variância por linearização de
Taylor (aproximação "com reposição" das UPAs dentro de cada estrato):

    u_i = w_i · (y_i − p·x_i) / X                      (variável linearizada)
    u_i ← u_i − w_i · ū_g,  ū_g = Σ_g u / Σ_g w        (ajuste de pós-estratificação, se houver)
    V(p) = Σ_h n_h/(n_h − 1) · Σ_j (U_hj − Ū_h)²       (U_hj = total da UPA j no estrato h)

IC 95% = p ± 1,96·EP, truncado em [0, 100] (como nas tabelas do IBGE). Estratos com uma
só UPA no domínio não contribuem para a variância (registrado em ``single_psu_strata``).

A implementação usa somas por índice inteiro (``numpy.bincount``) para calcular centenas
de domínios por indicador em poucos segundos.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

Z95 = 1.959963984540054


@dataclass(frozen=True)
class DesignArrays:
    """Arrays do desenho já codificados como inteiros 0..k-1."""

    weight: np.ndarray
    stratum: np.ndarray       # código do estrato por registro
    psu: np.ndarray           # código da UPA por registro (único no arquivo)
    psu_stratum: np.ndarray   # estrato de cada UPA
    poststratum: np.ndarray | None

    @classmethod
    def build(cls, weight, stratum_labels, psu_labels, poststrata_labels=None) -> "DesignArrays":
        _, h = np.unique(np.asarray(stratum_labels).astype(str), return_inverse=True)
        _, j = np.unique(np.asarray(psu_labels).astype(str), return_inverse=True)
        psu_h = np.zeros(j.max() + 1, dtype=np.int64)
        psu_h[j] = h
        g = None
        if poststrata_labels is not None:
            _, g = np.unique(np.asarray(poststrata_labels).astype(str), return_inverse=True)
        return cls(np.asarray(weight, dtype=float), h, j, psu_h, g)


@dataclass(frozen=True)
class Estimate:
    p: float              # proporção (0–1)
    se: float
    ci_lower: float
    ci_upper: float
    cv: float             # %
    n_den: int            # registros (não ponderados) no denominador
    n_num: int
    weighted_den: float
    psu_in_domain: int
    single_psu_strata: int


def ratio(design: DesignArrays, num: np.ndarray, den: np.ndarray) -> Estimate | None:
    """``num`` e ``den`` são 0/1 já restritos ao domínio (num ⊆ den)."""
    w = design.weight
    y = num.astype(float)
    x = den.astype(float)
    X = float(np.dot(w, x))
    if X <= 0:
        return None
    Y = float(np.dot(w, y))
    p = Y / X
    u = w * (y - p * x) / X
    if design.poststratum is not None:
        g = design.poststratum
        sw = np.bincount(g, weights=w)
        su = np.bincount(g, weights=u)
        mean = np.divide(su, sw, out=np.zeros_like(su), where=sw > 0)
        u = u - w * mean[g]
    U = np.bincount(design.psu, weights=u, minlength=len(design.psu_stratum))
    psu_h = design.psu_stratum
    # considera só as UPAs presentes na amostra (todas têm registro); n_h = nº de UPAs no estrato
    n_h = np.bincount(psu_h)
    sum_h = np.bincount(psu_h, weights=U)
    mean_h = np.divide(sum_h, n_h, out=np.zeros_like(sum_h), where=n_h > 0)
    dev2 = np.bincount(psu_h, weights=(U - mean_h[psu_h]) ** 2)
    factor = np.divide(n_h, n_h - 1, out=np.zeros(len(n_h)), where=n_h > 1)
    var = float(np.dot(factor, dev2))
    se = var ** 0.5
    in_dom = np.bincount(design.psu, weights=x, minlength=len(psu_h)) > 0
    dom_h = np.bincount(psu_h[in_dom], minlength=len(n_h))
    return Estimate(
        p=p, se=se, ci_lower=max(0.0, p - Z95 * se), ci_upper=min(1.0, p + Z95 * se),
        cv=(100 * se / p) if p > 0 else float("nan"),
        n_den=int(x.sum()), n_num=int(y.sum()), weighted_den=X,
        psu_in_domain=int(in_dom.sum()), single_psu_strata=int((dom_h == 1).sum()),
    )
