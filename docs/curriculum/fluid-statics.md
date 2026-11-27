# FM02 extended hydrostatics

Sources: [reading log 01](../research/phase-1-reading-notes-01.md), [University of Illinois MechRef statics](https://www.mechref.org/fluid/statics/?origin=coursemenu), [NPTEL IIT Kanpur statics recap](https://archive.nptel.ac.in/content/storage2/courses/112104118/recap/2_recapa.htm), and [Bar-Meir constant bulk modulus](https://eng.libretexts.org/Bookshelves/Civil_Engineering/Fluid_Mechanics_%28Bar-Meir%29/04%3A_Fluids_Statics/4.3%3A_Pressure_and_Density_in_a_Gravitational_Field/4.3.3_Varying_Density_in_a_Gravity_Field/4.3.3.2%3A_Liquid_Phase_Under_Hydrostatic_Pressure). Derivations independently checked in the reading log; no source text copied.

| API | Formula / model | Limits |
|---|---|---|
| pressure_path | sum(-rho*g*dz), also return final pressure | connected static path; constant-density segments, upward dz; no interface jump |
| gas_pressure | p0*exp(-g*dz/(R*T0)*log1p(x)/x), x=L*dz/T0 | ideal gas, constant g/R, linear T, positive absolute pressure and T |
| liquid_pressure_change | -K*log1p(-rho0*g*h/K) | ideal constant K; signed downward h; x<1, not a real-fluid EOS |
| plane_force | A*p_c | fully wetted plane with linear net pressure |
| plane_moment | rho*g*I*sin(theta) | one homogeneous fluid, uniform opposite pressure, downhill first moment |
| pressure_offset | M/F | signed offset from centroid, reject zero resultant |
| floating_fraction | rho_body/rho_fluid | homogeneous fluid, negligible gas buoyancy; equal densities give neutral full submergence, not surface stability |
| metacentric_height | KB-KG+I/V | initial small-angle flotation only, common datum and heel axis |
| translating_pressure_change | -rho*(ax*dx+(g+az)*dz) | rigid translation with constant acceleration, z upward |
| rotation_level_change | omega^2*(r2-r1)*(r2+r1)/(2g) | rigid rotation about vertical axis; no spill/dry floor model |

Scalar operations O(1) storage and work; pressure_path is O(n) time and O(1) auxiliary space via Neumaier compensated accumulation, returns delta separately to preserve small differences against a large absolute pressure. Local Python tracemalloc peaks 576 bytes for 1000 generated zero-height segments and 504 bytes for 100000 (single runs, excludes caller storage and total process RSS). Numerical stress example +1e16, +1, -1e16 Pa returns 1 Pa. Not a guarantee of accurate arbitrary extreme scales; validation rejects nonfinite intermediate floating values, integer overflow may raise.

Tests: 24 Python cases and 19 Node cases passed locally on isolated statics modules (prior repository files were not fully reconstructed). Shared fixtures include independent analytical values, signed cases and invalid domains; earlier reading log contains independent quadrature and ODE verification. Browser catalog integration and live smoke regression included; hosted CI pending. The pressure path is a Python/JS API, not an interactive browser form. General curved forces, layered buoyancy, arbitrary shape moments, partial immersion and tank volume constraints remain pending. All SI; no tagged units or real-fluid property lookup added.
