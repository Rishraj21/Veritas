# Veritas engineering curriculum roadmap

Status: approved direction and expanded subject scope from maintainer; technical release gates below. This is a staged development plan, not a claim of completed coverage or textbook review.

## Mission

Build a modular engineering computation and verification library. Support documented analytical calculators, numerical models, and independent verification of external results as distinct interfaces. Never conflate analytical agreement with experimental validation or safety certification.

## Shared foundation (ongoing, starting now)

SI units and dimension checks; material and fluid properties with provenance and validity ranges; vector/tensor conventions; numerical root finding, interpolation, integration, linear algebra, sparse matrices, ODE/PDE discretization, convergence and uncertainty; consistent errors and result metadata. Build only the foundation needed for the current phase. Retain existing check/reference API; avoid mandatory heavyweight dependencies until required. Optional numerical and property backends must be versioned and tested.

## Official implementation order (19 subjects)

Phase 0 is the numerical and computational foundation. Introduce shared optimization and uncertainty tools early; the full optimization domain is phase 18. The sequence is dependency-driven, not a claim of completion. Foundational ODE/PDE and linear algebra work may be staged when engineering examples are available; do not require a full general-purpose solver before implementing basic fluid properties.

| Phase | Subject | Scope |
|---|---|---|
| 0 | Numerical methods | Root finding, interpolation, quadrature, linear systems, eigenvalues, ODEs, PDE discretization, stability, error and convergence |
| 1 | Introductory fluid mechanics | Complete scoped inventory in docs/curriculum/fluid-mechanics.md; properties, hydrostatics, kinematics, balances, inviscid flow, dimensional analysis, internal/external flow, measurement, machinery, open channels, introductory gas dynamics |
| 2 | Engineering mechanics | Statics, free-body diagrams, equilibrium, trusses, friction, centroids, moments of inertia, kinematics, kinetics, impulse and energy |
| 3 | Strength of materials | Stress/strain, axial loading, torsion, bending, shear, deflection, stress transformation, failure criteria, columns, energy methods |
| 4 | Engineering thermodynamics | Properties, first/second laws, entropy, exergy, ideal/real gas, mixtures, power and refrigeration cycles; required thermo concepts introduced earlier for fluids and HMT |
| 5 | Heat and mass transfer | Conduction, transient conduction, convection, radiation, heat exchangers, diffusion, mass transfer and analogy correlations |
| 6 | Basic CFD | Finite differences, finite volumes, conservation, boundary conditions, diffusion/advection, pressure-velocity coupling, stability, mesh refinement, manufactured solutions; reproduce open solver cases |
| 7 | Basic FEA | Weak form, shape functions, quadrature, assembly, constraints, sparse linear systems, bar/truss/beam/plane elasticity, patch tests, mesh convergence |
| 8 | Mechanical vibrations | Free/forced and damped vibration, SDOF/MDOF systems, modal analysis, frequency response, isolation, continuous systems |
| 9 | Control systems | Transfer functions, state-space, stability, PID, frequency response, discrete control, controllability and observability |
| 10 | Refrigeration and cooling | Vapor compression/absorption, psychrometrics, cooling loads, component sizing and refrigerant property backends; distinguish estimates from code-compliant design |
| 11 | Turbomachinery | Velocity triangles, similarity, pumps, fans, compressors, turbines, performance maps and stage efficiency |
| 12 | Tribology | Contact mechanics, friction, wear, roughness, lubrication, Reynolds equation, bearing performance and correlation limits |
| 13 | Machine design | Shafts, springs, fasteners, gears, bearings, fatigue, failure criteria, design margins and standards-aware applicability |
| 14 | Advanced CFD | Turbulence modeling, compressible flow, higher-order schemes, unstructured meshes, transient flow, multiphase and coupled problems; prioritize verification and adapters rather than competing with production solvers |
| 15 | Advanced HMT | Conjugate transfer, variable properties, phase change, boiling, condensation, participating media, coupled species/energy |
| 16 | Advanced FEA | Geometric/material/contact nonlinearity, dynamics, modal/buckling analysis, fatigue/fracture, error estimation |
| 17 | Robotics | Rigid-body kinematics, rotations, Jacobians, dynamics, trajectories, control, estimation and simulation interfaces |
| 18 | Engineering optimization | Sensitivity, constrained/unconstrained optimization, multiobjective tradeoffs, uncertainty, reproducibility and model limitations |

## Foundation implementation sequence

- F0.1: consolidate existing SI conversions and validation; preserve public core/check API.
- F0.2: scalar root finding, quadrature, finite-difference differentiation, interpolation.
- F0.3: dense linear algebra, residual and conditioning diagnostics; use proven numerical backends for advanced sparse/eigenvalue algorithms rather than reinventing them.
- F0.4: ODE integration, error/stability analysis, introductory PDE discretization.
- F0.5: uncertainty, numerical convergence, basic optimization, property metadata.
- F0 gate: tested core numerical methods, documented limitations, reproducible examples and green CI; then begin fluid mechanics. Continue deeper foundation work as engineering modules require it.

See [numerical methods coverage ledger](docs/curriculum/numerical-methods.md). Pull required thermodynamic concepts forward for introductory compressible flow. No parallel expansion into unrelated subjects before the foundation and fluid releases are credible.

## Approved aggressive hybrid architecture

See [architecture and integration gates](docs/development/hybrid-architecture.md). Keep dependency-free baseline, optional compiled backends, structure-aware sparse/matrix-free methods, double precision defaults, independent residual checks and explicit memory/accuracy tradeoffs. Integrate experimentally verified techniques incrementally; do not present research prototypes as production features.

## Browser-first delivery

The initial product is a static browser application using ES modules, dedicated Web Workers, Float64Array storage, transferable result buffers and small WebAssembly kernels where measurements justify them. Python remains an independent reference and optional advanced backend, not a mandatory browser download. General partial eigenproblems use the optional SciPy/ARPACK adapter until a browser-native equivalent is validated. Do not add a mandatory remote execution service or upload user data without explicit opt-in. See [browser architecture](docs/development/browser-architecture.md).

## Package architecture

Keep a single Python distribution veritas-eng and namespace veritas. New numerical algorithms live under veritas.math; existing veritas.core, veritas.units and veritas.convergence remain modules to preserve compatibility. Domain subpackages such as veritas.fluids, veritas.cfd, veritas.solids, veritas.fea, veritas.heat, veritas.thermo and veritas.robotics; shared numerical/property layers. Existing analytical benchmark registry should call tested calculator functions rather than duplicate equations. Solvers and external adapters are separately named and optional. Use structured results and consistent units; maintain compatibility for current public API.

## Definition of done (per calculator/model)

- Traceable reference: title, edition, chapter/section and equation/page where available; access and license recorded.
- Independent implementation; mathematical facts are not a license to copy a textbook's prose, diagrams, code or protected tables.
- Clearly document equation, input/output units, sign conventions, assumptions, applicability and failure cases.
- Tests include independent hand-calculated or trusted reference values, limiting cases, invalid inputs, numerical residuals for implicit solutions, and physically meaningful invariants.
- Review numerical stability and uncertainty; empirical correlations require their range and provenance; no silent extrapolation.
- For numerical models, use analytical/manufactured solutions and convergence tests; for external verification, retain actual solver inputs, version, output and extraction method. Experimental validation is separate.
- Provide API and runnable example, CI green, and a coverage ledger. Only mark reviewed/implemented/tested when evidence exists.

Do not target arbitrary counts or artificially generate contributions. Build useful releases and invite genuine engineering reviews. A successful CI run alone is not proof of physical model validity.

## Immediate sprint

1. Implement and test the foundation numerical methods in small reviewable increments.
2. Finish dense linear algebra, ODE and diagnostics before the initial fluids release gate; use robust libraries for advanced production algorithms where appropriate.
3. Review legally accessible fluid mechanics sources chapter by chapter; record equations and assumptions before implementation.
4. Refactor existing pipe/Couette/Poiseuille benchmarks to reuse domain calculators with regression coverage.

The textbook chapter maps are preliminary; complete coverage must be supported by the ledger and verified tests.
