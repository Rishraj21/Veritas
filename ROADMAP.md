# Veritas engineering curriculum roadmap

Status: approved direction from maintainer; proposed technical refinements and gates below. This is a staged development plan, not a claim of completed coverage or textbook review.

## Mission

Build a modular engineering computation and verification library. Support documented analytical calculators, numerical models, and independent verification of external results as distinct interfaces. Never conflate analytical agreement with experimental validation or safety certification.

## Shared foundation (ongoing, starting now)

SI units and dimension checks; material and fluid properties with provenance and validity ranges; vector/tensor conventions; numerical root finding, interpolation, integration, linear algebra, sparse matrices, ODE/PDE discretization, convergence and uncertainty; consistent errors and result metadata. Build only the foundation needed for the current phase. Retain existing check/reference API; avoid mandatory heavyweight dependencies until required. Optional numerical and property backends must be versioned and tested.

## Curriculum and release gates

| Phase | Subject | Scope |
|---|---|---|
| 1 | Introductory fluid mechanics | Complete scoped inventory in docs/curriculum/fluid-mechanics.md; properties, hydrostatics, kinematics, balances, inviscid flow, dimensional analysis, internal/external flow, measurement, machinery, open channels, introductory gas dynamics |
| 2 | Basic CFD | Finite differences, finite volumes, conservation, boundary conditions, diffusion/advection, pressure-velocity coupling, stability, mesh refinement, manufactured solutions; reproduce open solver cases |
| 3 | Strength of materials | Stress/strain, axial loading, torsion, bending, shear, deflection, stress transformation, failure criteria, columns, energy methods |
| 4 | Basic FEA | Weak form, shape functions, quadrature, assembly, constraints, sparse linear systems, bar/truss/beam/plane elasticity, patch tests, mesh convergence |
| 5 | Heat and mass transfer | Conduction, transient conduction, convection, radiation, heat exchangers, diffusion, mass transfer and analogy correlations |
| 6 | Engineering thermodynamics | Properties, first/second laws, entropy, exergy, ideal/real gas, mixtures, power and refrigeration cycles; required thermo concepts introduced earlier for fluids and HMT |
| 7 | Advanced CFD | Turbulence modeling, compressible flow, higher-order schemes, unstructured meshes, transient flow, multiphase and coupled problems; prioritize verification and adapters rather than competing with production solvers |
| 8 | Advanced HMT | Conjugate transfer, variable properties, phase change, boiling, condensation, participating media, coupled species/energy |
| 9 | Advanced FEA | Geometric/material/contact nonlinearity, dynamics, modal/buckling analysis, fatigue/fracture, error estimation |
| 10 | Refrigeration and cooling | Vapor compression/absorption, psychrometrics, cooling loads, component sizing and refrigerant property backends; distinguish estimates from code-compliant design |
| 11 | Robotics | Rigid-body kinematics, rotations, Jacobians, dynamics, trajectories, control, estimation and simulation interfaces |

Keep the user's order, with prerequisites pulled forward when necessary. Proposed additions after or alongside the curriculum: engineering statics/dynamics, mechanical vibrations and controls before robotics, turbomachinery as a continuation of fluids, machine design/fatigue, tribology, and uncertainty/optimization as shared tools. Do not expand scope until the first fluid-mechanics milestone meets its release gate.

## Architecture proposal

Keep a single Python distribution veritas-eng and namespace veritas. Domain subpackages such as veritas.fluids, veritas.cfd, veritas.solids, veritas.fea, veritas.heat, veritas.thermo and veritas.robotics; shared numerical/property layers. Existing analytical benchmark registry should call tested calculator functions rather than duplicate equations. Solvers and external adapters are separately named and optional. Use structured results and consistent units; maintain compatibility for current public API.

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

1. Review legally accessible fluid mechanics sources chapter by chapter; record formula inventory and assumptions.
2. Implement the fluid properties and statics calculator families first, then move through the scoped inventory.
3. Refactor existing pipe/Couette/Poiseuille benchmark formulas to reuse domain calculators with regression coverage.
4. Add unit coverage, reference examples, numerical root-finding for implicit friction/flow problems, and CI tests as needed.
5. Release a usable fluids package before broadening to CFD.

Current repository remains an early prototype. The textbook chapter map is preliminary and has not been exhaustively reviewed. No commitment to reading or implementation in the background.
