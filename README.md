# Veritas

**Open-source engineering computation and simulation verification.**

Veritas compares scalar outputs from a simulation with transparent closed-form reference solutions. It also includes educational numerical solvers; it is not a certification system or a replacement for experimental validation. A passing comparison applies only to the specified benchmark, assumptions and tolerance.

## Browser-first numerical laboratory

No Python package or network service is required for the local browser solvers. From the repository root, run:

```sh
python -m http.server 8000 --directory web
```

Open http://localhost:8000 in a modern browser. The Poisson benchmark runs geometric multigrid, JS matrix-free CG or a WASM stencil-backed CG in a dedicated worker with cancellation and a numerical-buffer budget. The local-file tool streams little-endian Float64 values. CSR and tensor contractions are available as worker/library APIs. General symmetric partial eigenpairs are provided by the optional Python/SciPy adapter, not a browser endpoint. See [browser architecture](docs/development/browser-architecture.md). Numerical kernels tested with `node --test tests/browser.test.mjs`; full UI smoke test is configured separately.

## Quick start

Python 3.10+; no mandatory runtime dependencies. Optional acceleration is available. The distribution is named `veritas-eng`; Python imports and the CLI remain `veritas`. Install from this repository:

```sh
git clone https://github.com/Rishraj21/Veritas.git
cd Veritas
python -m pip install .
veritas list
veritas describe cantilever_tip
veritas validate examples/passing.json
veritas validate examples/demo.json --json
```

The demo intentionally includes one failed check. Exit codes: `0` all checks pass, `1` at least one check fails, `2` invalid input or CLI usage. Numeric inputs default to the documented SI units. Explicit tagged quantities are checked against a limited, dimension-specific unit whitelist and converted to SI. Unsupported units are rejected; general unit-expression parsing is not supported.

## Unit-aware JSON and CSV

```sh
veritas validate examples/beam_units.json --json
veritas validate examples/beam_units.csv --json
```

A quantity may be a number in SI or an object such as `{"value": 200, "unit": "GPa"}`. The same applies to observed values and absolute tolerance. Absolute temperature uses `degC`/`degF`; temperature tolerance uses `delta_degC`/`delta_degF` or `K`. Relative tolerance is dimensionless and always refers to the reference expressed in SI.

CSV uses one case per row: `benchmark`, `observed`, optional `id`, `observed_unit`, `rtol`, `atol`, `atol_unit`, and `param.NAME` plus optional `param.NAME.unit` columns. Blank columns for parameters belonging to other benchmarks are permitted, but unexpected nonblank parameters, duplicate headers and malformed rows are rejected. See [input format](docs/input-format.md) for details.

## Python API

```python
from veritas import check, estimate_order

result = check('cantilever_tip', {
    'force': 300, 'length': 2, 'youngs_modulus': 200e9,
    'second_moment': 1e-6,
}, observed=0.00401, rtol=0.01)
print(result.passed, result.expected)
print(estimate_order(1, .5, .25, 5, 2, 1.25))
```

The acceptance rule is `abs(observed - reference) <= atol + rtol * abs(reference)`. Absolute tolerance is expressed in the output unit. Relative error is undefined for zero reference and reported as `null`. The three-grid routine estimates observed order and Richardson extrapolation only for monotonically convergent, uniformly refined grids under a leading-power error assumption. It is not a grid-convergence index or proof of asymptotic convergence.

## Benchmark catalogue (v0.1)

| ID | Reference quantity |
|---|---|
| `pipe_flow` | Hagen–Poiseuille volumetric flow rate |
| `couette_flow` | Plane Couette velocity |
| `plane_poiseuille` | Parallel-plate pressure-driven velocity |
| `axial_bar` | Axial displacement |
| `cantilever_tip` | End-loaded cantilever deflection |
| `circular_shaft` | Solid circular shaft angle of twist |
| `slab_conduction` | Steady plane-wall heat transfer rate |
| `lumped_cooling` | Lumped body temperature |
| `spring_mass` | Undamped natural frequency |
| `insulated_fin` | Adiabatic-tip fin base heat transfer |

Use `veritas describe <id>` for formulas, units and assumptions. See [benchmark notes](docs/benchmarks.md) for source references and scope. Example observations are synthetic, not measured solver output.

## Independent numerical example

Run `python examples/radial_fvm.py` for a reproducible finite-volume pipe-flow solve on four grids, followed by an analytical comparison and observed convergence order. See [numerical example](docs/numerical-example.md). It is an educational numerical solver, not an OpenFOAM/CalculiX integration.

## Numerical methods

```python
from veritas.math import bisection, simpson, derivative, linear_interpolate

root = bisection(lambda x: x*x - 2, 1, 2)
assert root.converged
area = simpson(lambda x: x*x, 0, 1, n=100)
slope = derivative(lambda x: x*x, 3, h=1e-4)
value = linear_interpolate([0, 2], [10, 20], 1)
```

Small educational numerical algorithms with explicit limits; see the numerical methods coverage ledger for assumptions and test status.

```python
from veritas.math import solve_linear, solve_ivp, error_norms, stability_factor

linear = solve_linear([[0, 2], [1, 3]], [4, 7], condition=True)
print(linear.solution, linear.backward_error, linear.condition_inf)

ode = solve_ivp(lambda t, y: -2*y, (0, 1), 1.0, n=100, method="rk4")
print(ode.y[-1], ode.evaluations)
```

The linear solver uses scaled partial-pivoted LU and provides residual diagnostics. Fixed-step ODE solvers support scalar and vector systems with Euler, midpoint, Heun and RK4. They are not adaptive or suitable for general stiff problems. Run `python examples/numerical_foundation.py` for a reproducible example.

### Structured linear systems and repeated interpolation

```python
from veritas.math import Tridiagonal, stationary_solve, LinearInterpolator

a = Tridiagonal([-1, -1], [4, 4, 4], [-1, -1])
factor = a.factor()
x = factor.solve([3, 2, 3])
iterative = stationary_solve(a, [3, 2, 3], method="gauss_seidel")
p = LinearInterpolator([0, 10, 20], [100, 120, 140])
print(x, iterative.converged, p(5))
```

Thomas elimination uses three diagonal arrays, not a dense matrix. It requires safe pivots; iterative methods do not guarantee convergence. Reuse the factors or interpolator for repeated queries. Run `python examples/structured_solvers.py` to compare measured allocations and residuals.

### One-dimensional PDE foundation

```python
from math import sin, pi
from veritas.math import heat_1d, poisson_1d

x, u = poisson_1d(lambda x: 2, cells=100)
result = heat_1d(lambda x: sin(pi*x), diffusivity=0.1,
                 duration=0.1, cells=100, steps=100, store_every=100)
```

Uniform grids, constant coefficients and fixed Dirichlet boundaries only. The implicit schemes reuse a tridiagonal factorization; output retention is configurable. See the numerical methods ledger and `python examples/diffusion_memory.py` for the measured allocation comparison.

### Adaptive ODE integration

```python
from veritas.math import rk23

r = rk23(lambda t, y: -2*y, (0, 3), 1, rtol=1e-6,
         atol=1e-9, store_every=100000)
assert r.converged
print(r.y[-1], r.accepted, r.rejected, r.evaluations)
```

Embedded RK3(2) with local error control and reused endpoint derivatives. Nonstiff problems only; no guaranteed global error bound. See the numerical methods ledger and `python examples/adaptive_memory.py`.

### Matrix-free conjugate gradient

```python
from veritas.math import conjugate_gradient, PoissonStencil2D

a = PoissonStencil2D(100, 100)
result = conjugate_gradient(a, (1.0 for _ in range(10000)))
assert result.converged
print(result.residual_l2)
```

Packed buffers and an in-place operator API avoid matrix assembly and iteration history. CG is only for symmetric positive definite systems; the example uses an unscaled discrete Laplacian with homogeneous Dirichlet conditions. See the ledger and `python examples/matrix_free_memory.py` for the measured memory/runtime trade-off.

### Hybrid acceleration

Install optional dependencies with `python -m pip install '.[jit]'` (or `.[accelerated]` without Numba).

```python
from veritas.math import poisson_operator, solve_sparse

a = poisson_operator(32, 32, compiled=True)
r = solve_sparse(a, [1.0]*1024, spd=True)
assert r.converged
```

Sparse and matrix-free SciPy solvers, explicit SPD selection, BiCGSTAB-to-GMRES fallback and an optional Krylov-basis budget. See the [hybrid architecture](docs/development/hybrid-architecture.md) for scope, test evidence and remaining integrations.

## Engineering curriculum

The [roadmap](ROADMAP.md) defines the staged expansion from introductory fluid mechanics through CFD, solids, FEA, thermal sciences and robotics. Phase 0 is the [numerical methods foundation](docs/curriculum/numerical-methods.md), followed by the [fluid mechanics coverage plan](docs/curriculum/fluid-mechanics.md). These are planned capabilities, not claims of current coverage.

## Development

```sh
python -m pip install -e '.[test]'
python -m pytest -q
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for benchmark proposals, review standards and planned integrations. MIT licensed. This is an early prototype. The planned PyPI distribution is `veritas-eng`. It has not been published by this project yet; install from GitHub for now. Do not install the unrelated PyPI package `veritas`.
