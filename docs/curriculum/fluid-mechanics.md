# Phase 1: introductory fluid mechanics coverage plan

## Source strategy

Use the following publisher/course outlines to define breadth, then read accessible full chapters and independent references before implementing individual equations. These are coverage references, not a claim of full-text review.

- Fox and McDonald's Introduction to Fluid Mechanics, 10th ed. (Wiley): https://www.wiley.com/en-us/shop/general-introductory-mechanical-engineering/fox-and-mcdonald%27s-introduction-to-fluid-mechanics-10th-edition-p-9781119603764
- Munson, Young and Okiishi's Fundamentals of Fluid Mechanics, 9th ed. (Wiley): https://www.wiley.com/en-us/munson-young-and-okiishi%27s-fundamentals-of-fluid-mechanics-9th-edition-p-9781119686538
- Genick Bar-Meir, Basics of Fluid Mechanics (open textbook record): https://mds.marshall.edu/oa-textbooks/69/
- MIT OCW 2.06 Fluid Dynamics: https://ocw.mit.edu/courses/2-06-fluid-dynamics-spring-2013/
- NASA Glenn verification guidance: https://www.grc.nasa.gov/www/wind/valid/tutorial/tutorial.html

## Coverage ledger (proposed families, not exhaustive equation list)

| ID | Family | Planned calculator/model coverage | Status |
|---|---|---|---|
| FM01 | Properties and dimensions | Density, specific weight/gravity/volume, Newtonian shear, dynamic/kinematic viscosity, bulk modulus, compressibility, surface tension, Laplace pressure, capillary rise, dimensionless groups | Partial: scalar property models implemented; local tests passed |
| FM02 | Hydrostatics | Hydrostatic pressure, gauge/absolute pressure, layered fluids, manometers, plane forces and centers of pressure, curved surface components, buoyancy, flotation, metacentric height, rigid-body acceleration/rotation | Partial: pressure, head, buoyancy implemented; local tests passed |
| FM03 | Kinematics | Velocity and acceleration fields, material derivatives, divergence, vorticity, circulation, strain-rate tensor, streamfunction, streamline integration | Planned |
| FM04 | Integral balances | Mass flow, continuity, momentum forces on nozzles/bends/jets, reaction, torque, mechanical energy, shaft power, control-volume sign conventions | Planned |
| FM05 | Inviscid flow | Euler and Bernoulli relations with assumptions, stagnation pressure, hydraulic/energy grade lines, ideal flow elements and superposition | Planned |
| FM06 | Dimensional analysis | Reynolds, Froude, Mach, Weber, Euler, Strouhal, cavitation number, Buckingham Pi via rank/nullspace, model scaling | Planned |
| FM07 | Laminar internal flow | Pipe/plane Poiseuille and Couette profiles, mean/max velocities, flow and pressure drop, wall shear, hydraulic diameter, entrance length estimates | Existing three benchmarks; calculator refactor planned |
| FM08 | Pipe systems | Darcy-Weisbach, Darcy/Fanning distinction, minor loss, friction factors, Colebrook root solver, roughness and range checks, series/parallel networks, pump-system intersections | Planned |
| FM09 | Flow measurement | Pitot, Venturi, orifice, nozzle, discharge coefficients, uncertainty, weirs and flumes | Planned |
| FM10 | External flows | Boundary-layer thicknesses, momentum/displacement thickness, laminar/turbulent skin friction within ranges, drag, lift, Stokes flow and terminal velocity | Planned |
| FM11 | Hydraulic machines | Pump and turbine power, efficiencies, head, affinity laws, Euler turbomachinery equation, specific speed conventions, NPSH, cavitation limits | Planned |
| FM12 | Open-channel hydraulics | Hydraulic radius, Manning/Chezy, specific energy, critical/normal depth, Froude, hydraulic jump, gradually varied flow | Planned |
| FM13 | Introductory gas dynamics | Ideal-gas properties, sound speed, Mach, stagnation state, isentropic area/Mach, choking, normal shocks; pull forward needed thermodynamics | Planned |
| FM14 | Differential flow and numerical bridge | Conservation PDEs, stress tensor, canonical exact solutions, simple discretizations, verification examples; general Navier-Stokes is not a scalar calculator | Planned |
| FM15 | Measurements and uncertainty | Propagation of measurement uncertainty, sensitivity, residuals, error norms, applicability and verification | Planned |

## First implementation batch

Start with properties and statics: density/specific weight/volume, dynamic/kinematic viscosity, shear stress, bulk modulus, surface-tension pressure jump, capillary rise, pressure versus depth, pressure head, layered columns, buoyancy and planar hydrostatic forces. Separate signed conventions from magnitudes; reject invalid absolute pressures only when the model specifically requires them. Support SI values and explicitly tagged quantities.

## Tracking

For each equation, add a ledger entry with identifier, source section, formula, domain limits, API name, reference example, test path, review status. Do not infer that an entire chapter is complete because one equation is implemented. Equivalent rearrangements should generally reuse the same physical model, and implicit inversions should report residual and convergence instead of hiding failure.

Use independent formulas and original explanations. Do not reproduce proprietary property tables, figures or worked examples without rights. When a physical property library is necessary, use a vetted backend with documented license, version, valid ranges and uncertainty.

See [FM01 and initial FM02 equation ledger](fluid-properties.md) for reference sources, formulas, assumptions and tests.
