# Veritas

**Solver-independent analytical verification checks for engineering simulations.**

Veritas compares scalar outputs from a simulation with transparent closed-form reference solutions. It is intentionally not a solver, a certification system, or a replacement for experimental validation. A passing comparison applies only to the specified benchmark, assumptions and tolerance.

## Quick start

Python 3.10+; no runtime dependencies. From this source tree:

```sh
python -m pip install .
physcheck list
physcheck describe cantilever_tip
physcheck validate examples/passing.json
physcheck validate examples/demo.json --json
```

The demo intentionally includes one failed check. Exit codes: `0` all checks pass, `1` at least one check fails, `2` invalid input or CLI usage. All parameters and observations must already be in the documented SI units; unit conversion and dimensional validation are not yet implemented.

## Python API

```python
from physcheck import check, estimate_order

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

Use `physcheck describe <id>` for formulas, units and assumptions. See [benchmark notes](docs/benchmarks.md) for source references and scope. Example observations are synthetic, not measured solver output.

## Development

```sh
python -m pip install -e '.[test]'
python -m pytest -q
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for benchmark proposals, review standards and planned integrations. MIT licensed. This is an early prototype; the Python distribution name has not been checked for PyPI availability.
