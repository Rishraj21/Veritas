"""One-dimensional finite differences on a uniform grid.

Constant coefficients and fixed Dirichlet boundary values only. Implicit
schemes reuse a tridiagonal factorization; no dense matrices are formed.
"""
from dataclasses import dataclass
from ._validation import finite, positive, count, evaluate
from .banded import Tridiagonal


@dataclass(frozen=True, slots=True)
class HeatResult:
    x: tuple
    t: tuple
    u: tuple
    diffusion_number: float
    method: str


def _grid(length, cells):
    length = positive(length, "length")
    cells = count(cells, "cells", 2)
    dx = positive(length/cells, "grid spacing")
    return tuple(length*(i/cells) for i in range(cells+1)), dx


def poisson_1d(source, *, length=1.0, cells=100, left=0.0, right=0.0):
    """Solve -u''=source(x) with fixed endpoint values; return (x,u).

    Second-order spatial truncation for smooth solutions. O(cells) work
    and storage; no general variable-coefficient or Neumann support.
    """
    x, dx = _grid(length, cells)
    left, right = finite(left, "left"), finite(right, "right")
    n = cells-1
    rhs = [finite(dx*(dx*evaluate(source, xi)), "source term") for xi in x[1:-1]]
    rhs[0] = finite(rhs[0]+left, "boundary source")
    rhs[-1] = finite(rhs[-1]+right, "boundary source")
    factor = Tridiagonal([-1]*(n-1), [2]*n, [-1]*(n-1)).factor()
    return x, (left, *factor.solve(rhs), right)


def heat_1d(initial, *, diffusivity, length=1.0, duration, cells=100,
            steps=100, left=0.0, right=0.0, method="crank_nicolson", store_every=1):
    """Solve u_t=diffusivity*u_xx, fixed Dirichlet endpoints, no source.

    FTCS requires r=alpha*dt/dx^2 <= 1/2. Backward Euler and Crank-Nicolson
    are unconditionally stable in the linear diffusion sense, not necessarily
    accurate; Crank-Nicolson can oscillate for large r. Initial callable is
    sampled only at interior nodes; endpoints are imposed at all times.
    Keep every kth state and both endpoints, independent of integration steps.
    """
    theta_by_method = {"explicit": 0.0, "backward_euler": 1.0, "crank_nicolson": 0.5}
    if method not in theta_by_method:
        raise ValueError("Unknown heat method")
    theta = theta_by_method[method]
    x, dx = _grid(length, cells)
    steps = count(steps, "steps")
    store_every = count(store_every, "store_every")
    duration = positive(duration, "duration")
    alpha = positive(diffusivity, "diffusivity")
    left, right = finite(left, "left"), finite(right, "right")
    dt = positive(duration/steps, "time step")
    r = positive((alpha/dx)*(dt/dx), "diffusion number")
    if theta == 0 and r > 0.5:
        raise ValueError("Explicit heat scheme requires diffusion number <= 0.5")
    n = cells-1
    current = tuple(evaluate(initial, xi) for xi in x[1:-1])
    factor = None
    if theta:
        band = -theta*r
        factor = Tridiagonal([band]*(n-1), [finite(1+2*theta*r,"diagonal")]*n,
                             [band]*(n-1)).factor()
    saved_t = [0.0]
    saved_u = [(left, *current, right)]
    explicit_weight = (1-theta)*r
    for step in range(1, steps+1):
        rhs = []
        for i, value in enumerate(current):
            west = current[i-1] if i else left
            east = current[i+1] if i+1<n else right
            # The implicit boundary contributions are moved to the RHS below.
            rhs.append(finite(value+explicit_weight*((west-value)+(east-value)), "heat RHS")
                       if explicit_weight else value)
        if factor is not None:
            rhs[0] = finite(rhs[0]+theta*r*left, "boundary source")
            rhs[-1] = finite(rhs[-1]+theta*r*right, "boundary source")
            current = factor.solve(rhs)
        else:
            current = tuple(rhs)
        if step % store_every == 0 or step == steps:
            saved_t.append(duration*(step/steps))
            saved_u.append((left, *current, right))
    return HeatResult(x, tuple(saved_t), tuple(saved_u), r, method)
