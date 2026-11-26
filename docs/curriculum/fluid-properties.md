# FM01 and initial FM02 — scalar models

Theory references (accessible HTML, original implementation):
- OpenStax University Physics Volume 1, [14.1 Fluids, Density and Pressure](https://openstax.org/books/university-physics-volume-1/pages/14-1-fluids-density-and-pressure), [chapter 14 equations](https://openstax.org/books/university-physics-volume-1/pages/14-key-equations).
- OpenStax College Physics, [11.8 Surface Tension and Capillary Action](https://openstax.org/books/college-physics/pages/11-8-cohesion-and-adhesion-in-liquids-surface-tension-and-capillary-action).
- [MechRef introductory incompressible flow](https://www.mechref.org/fluid/introduction/) and [Fluid Statics](https://www.mechref.org/fluid/statics/).

| Model | Equation | Limits |
|---|---|---|
| density | m/V | positive mass and volume |
| specific_volume | 1/rho | positive density |
| specific_weight | rho*g | positive gravitational magnitude |
| specific_gravity | rho/rho_ref | reference density explicit; temperature and pressure chosen by caller |
| kinematic_viscosity | mu/rho | positive dynamic viscosity |
| shear_stress | mu*du/dy | Newtonian simple shear; signed gradient |
| compressibility | 1/K | bulk modulus and compressibility on same thermodynamic path |
| volume_strain | -delta_p/K | linearized small strain only; no finite compression model |
| laplace_pressure | sigma*(1/R1+1/R2) | one interface; signed curvature consistent with jump convention; soap bubbles require two interfaces |
| capillary_rise | 2*sigma*cos(theta)/(r*delta_rho*g) | static circular tube, angle measured through denser liquid, meniscus approximation; signed rise/depression |
| hydrostatic_pressure | p0+rho*g*h | constant density and gravity, depth positive down, datum unchanged |
| pressure_head | p/(rho*g) | signed pressure with caller-selected datum |
| buoyancy | rho*g*Vdisplaced | upward force magnitude, constant density |

All inputs SI, including angles in radians. Standard gravity default 9.80665 m/s^2 in Python; browser explicitly displays the value. No automatic material property lookup or tagged-unit conversion in these new APIs. Input density, viscosity, surface tension and modulus must correspond to the actual fluid state. Browser defaults are illustrative, not a validated property table. Extreme numerical scales can overflow or underflow. The browser evaluates scalar equations directly (constant auxiliary storage, no worker or WASM startup); heavy PDE computations remain in workers. Python and JavaScript implementations share independent reference fixtures, not generated expected values from one another.

Local sandbox: 21 Python cases and 17 Node test cases passed, including signed shear, capillary depression, negative pressure head, zero displacement, invalid inputs and catalog defaults. Python tested the new package and exact existing validation helper, not the entire repository. Full CI and browser UI smoke pending at initial push.

Remaining FM01: dimensional analysis (FM06), property state correlations and inversions. Remaining FM02: layered columns, manometers, plane/curved force, flotation stability, accelerating/rotating tanks. Do not mark whole chapters complete.
