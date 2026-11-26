"""Three-grid observed order and Richardson extrapolation.

Only for scalar, monotonic, nonzero differences on three uniformly refined
meshes, under an assumed leading-power asymptotic error model. Not a GCI.
"""
from math import log, isclose
from .benchmarks import finite_number


def estimate_order(h_coarse, h_medium, h_fine, q_coarse, q_medium, q_fine):
    hc, hm, hf, qc, qm, qf = [finite_number(x, "mesh input") for x in (h_coarse, h_medium, h_fine, q_coarse, q_medium, q_fine)]
    if not hc > hm > hf > 0:
        raise ValueError("Grid spacings must be positive and strictly decreasing")
    r = hc/hm
    if not isclose(r, hm/hf, rel_tol=1e-6):
        raise ValueError("A constant grid refinement ratio is required")
    d1, d2 = qc-qm, qm-qf
    if d1 == 0 or d2 == 0 or (d1 > 0) != (d2 > 0):
        raise ValueError("Differences must be nonzero and have the same sign")
    p = log(abs(d1/d2))/log(r)
    if p <= 0:
        raise ValueError("No positive observed order; asymptotic convergence not established")
    extrap = qf + (qf-qm)/(r**p-1)
    return {"observed_order": finite_number(p, "observed order"), "extrapolated_value": finite_number(extrap, "extrapolated value"), "refinement_ratio": finite_number(r, "refinement ratio")}
