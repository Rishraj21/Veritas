"""Independent radial finite-volume discretization of fully developed pipe flow.

Solve -d(r du/dr)/dr = r dp/(mu L) on 0 <= r <= R. Cell-centred annuli,
zero flux at the axis, zero velocity at the wall (half-cell distance).
The tridiagonal system is solved numerically; the solver never calls the
analytical benchmark. Annular quadrature gives the volumetric flow rate.
This is a small educational solver, not OpenFOAM or a general CFD code.
"""
import json
from math import isfinite, pi
from veritas import check, estimate_order


def solve_pipe(n, *, radius, length, viscosity, pressure_drop):
    if isinstance(n, bool) or not isinstance(n, int) or n < 2:
        raise ValueError("At least two radial cells are required")
    if not all(isfinite(x) and x > 0 for x in (radius, length, viscosity)):
        raise ValueError("Positive finite radius, length and viscosity required")
    if not isfinite(pressure_drop):
        raise ValueError("Finite pressure drop required")
    h = radius/n
    lower, diag, upper, rhs, weights = [], [], [], [], []
    for i in range(n):
        inner, outer = i*h, (i+1)*h
        annulus = outer**2 - inner**2
        west = inner/h
        east = outer/(h/2 if i == n-1 else h)
        lower.append(-west)
        diag.append(west+east)
        upper.append(-east if i < n-1 else 0.0)
        rhs.append(pressure_drop/(viscosity*length)*annulus/2)
        weights.append(pi*annulus)
    # Thomas algorithm: eliminate subdiagonal, then back substitute.
    for i in range(1,n):
        multiplier = lower[i]/diag[i-1]
        diag[i] -= multiplier*upper[i-1]
        rhs[i] -= multiplier*rhs[i-1]
    velocity = [0.0]*n
    velocity[-1] = rhs[-1]/diag[-1]
    for i in range(n-2,-1,-1):
        velocity[i] = (rhs[i]-upper[i]*velocity[i+1])/diag[i]
    return sum(w*u for w,u in zip(weights,velocity))


def run_demo():
    params = dict(radius=.001, length=1.0, viscosity=.001, pressure_drop=1000.)
    rows = []
    for n in (8,16,32,64):
        q = solve_pipe(n,**params)
        result = check("pipe_flow",params,q,rtol=.005)
        rows.append({"cells":n,"grid_spacing":params["radius"]/n,**result.to_dict()})
    last = rows[-3:]
    convergence = estimate_order(
        *(row["grid_spacing"] for row in last),
        *(row["observed"] for row in last))
    return {"provenance":"independent radial finite-volume solve; no external solver",
            "parameters_si":params,"results":rows,"convergence":convergence}


if __name__ == "__main__":
    print(json.dumps(run_demo(),indent=2,allow_nan=False))
