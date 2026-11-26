# Veritas

**Solver-independent analytical verification checks for engineering simulations.**

Veritas compares scalar outputs from a simulation with transparent closed-form reference solutions. It is intentionally not a solver, a certification system, or a replacement for experimental validation. A passing comparison applies only to the specified benchmark, assumptions and tolerance.

## Quick start

Python 3.10+; no runtime dependencies. The distribution is named `veritas-eng`; Python imports and the CLI remain `veritas`. Install from this repository:

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

## Development

```sh
python -m pip install -e '.[test]'
python -m pytest -q
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for benchmark proposals, review standards and planned integrations. MIT licensed. This is an early prototype. The planned PyPI distribution is `veritas-eng`. It has not been published by this project yet; install from GitHub for now. Do not install the unrelated PyPI package `veritas`.
