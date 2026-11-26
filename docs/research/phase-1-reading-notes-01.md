# Phase 1 textbook reading log 01 — properties, statics and integral balances

Date: 2026-11-27. This is a substantive section-level reading and mathematical audit, not a cover-to-cover completion certificate. The commercial books in the main bibliography retain their actual reading statuses. No third-party book PDFs, tables, diagrams or example text are redistributed. All equations below are independently expressed engineering mathematics.

## Access and sections actually examined

| Source | Access and material inspected | What remains |
|---|---|---|
| Genick Bar-Meir, Basics of Fluid Mechanics, older open web edition (2010 mirror) | [Author's open-content release information](https://www.bar-meir.com/downloads.php); [readable PDF mirror](https://nzdr.ru/data/media/biblio/kolxoz/P/PC/PCfm/Bar-Meir%20G.%20Basics%20of%20Fluid%20Mechanics%20%28free%20web%20version%2C%202010%29%28282s%29_PCfm_.pdf). Text inspected around §§1.5.2–1.5.5, 4.3.1–4.3.3, 4.4, 4.5.1–4.5.2, 4.6.1, 5.3 and 6.1.3–6.1.5 (selected equations and examples, printed pp. 10–20, 57–64, 72–87, 99–104, 127, 145–147). | Other pages and newer complete edition; screenshot retrieval failed, so no visual verification of diagrams. |
| W. P. Graebel, Engineering Fluid Mechanics, International Student Edition, Taylor & Francis (2001; e-library 2008) | [Commercial book preview](https://api.pageplace.de/preview/DT0400.9781482284751_A35719161/preview-9781482284751_A35719161.pdf), Ch. 2 §§1–2, printed pp. 41–53, substantive hydrostatic force derivation, gas atmosphere and manometers; selected Ch. 1 end-of-chapter rheology material. | Preview stops during Ch. 2; remaining chapters inaccessible here; screenshot retrieval failed. |
| Moebs, Ling, Sanny, University Physics Vol. 1 | [§14.1](https://openstax.org/books/university-physics-volume-1/pages/14-1-fluids-density-and-pressure), [§14.4](https://openstax.org/books/university-physics-volume-1/pages/14-4-archimedes-principle-and-buoyancy), [§14.6](https://openstax.org/books/university-physics-volume-1/pages/14-6-bernoullis-equation) (substantive text on pressure, buoyancy, and ideal energy). | Not a sufficient source for empirical engineering correlations. Current page license notice identifies CC BY-NC-SA; do not reproduce or redistribute its text/tables. |
| DOE Fundamentals Handbook DOE-HDBK-1012/3-92 (1992) | Public HTML reproduction: [continuity](https://engineeringlibrary.org/reference/continuity-equation-fluid-flow-doe-handbook), [Bernoulli](https://engineeringlibrary.org/reference/bernoullis-equation-fluid-flow-doe-handbook), [head loss](https://engineeringlibrary.org/reference/head-loss-fluid-flow-doe-handbook), [centrifugal pumps](https://engineeringlibrary.org/reference/centrifugal-pumps-fluid-flow-doe-handbook). Inspected substantive sections on these concepts, including eq. 3-14 Darcy loss and eqs. 3-8–3-11 energy derivation. | Complete chapter traversal and modern correlation comparisons remain outstanding. Handbook uses US customary examples; derive SI form independently. |
| James Liburdy, Intermediate Fluid Mechanics, Oregon State University (2021) | [Chapter index](https://eng.libretexts.org/Bookshelves/Civil_Engineering/Intermediate_Fluid_Mechanics_%28Liburdy%29), [Ch. 5 integral boundary layer](https://eng.libretexts.org/Bookshelves/Civil_Engineering/Intermediate_Fluid_Mechanics_%28Liburdy%29/05%3A_Integral_Boundary_Layer_Relationships), [Ch. 7 panel method](https://eng.libretexts.org/Bookshelves/Civil_Engineering/Intermediate_Fluid_Mechanics_%28Liburdy%29/07%3A_The_Panel_Method_-_An_Introduction), substantive indexed excerpts. | Direct Oregon State host returned 403; complete text and remaining chapters not reviewed. CC BY-NC-SA 4.0: use only original mathematical implementation, no copied prose/code. |
| Christoph Rapp, Hydraulics in Civil Engineering (Springer 2024) | [Open-access book](https://doi.org/10.1007/978-3-031-54860-4), chapter abstracts for Ch. 7, 8, 11, 13 and contents. | Full chapter PDFs returned cache errors. Metadata/abstract status only; cannot claim substantive reading. |

## Independent derivation decisions for FM01 and FM02

Use z positive upward, g positive magnitude, h positive downward; all pressures in Pa. Density and constitutive properties are state-dependent inputs. Avoid silently selecting incompressibility for large gas columns or deep liquids.

### Hydrostatic balance and manometers

Force balance of a differential volume gives grad(p)=rho*g_vector for a static fluid. In a constant-density vertical segment, p_B-p_A=-rho*g*(z_B-z_A). For any piecewise-constant connected path, sum these signed increments, with an explicit interface pressure jump if surface tension matters. Use compensated accumulation and return both delta_p and final pressure; avoid subtracting two large absolute pressures to recover a small difference. Equal elevation is an equal-pressure condition only within a connected stationary homogeneous fluid (or the appropriate equipotential); it is not a universal rule across unrelated fluids.

Gauge vs absolute datum: p_abs=p_gauge+p_atm. Gauge pressure can be negative. For ideal gas models require p_abs>0. For a vapor-capped barometer, p_atm=p_v+rho*g*h; neglect p_v only when justified. Layered columns and manometers are one canonical path integral, not dozens of geometry-specific formulas. Complexity O(number of segments), O(1) auxiliary memory.

### Compressible hydrostatics

Isothermal ideal gas: dp/dz=-(g/(R*T))*p, hence p=p0*exp(-g*dz/(R*T)). For a specified linear temperature T=T0+L*dz, integrate to obtain ln(p/p0)=-(g/(R*L))*log1p(L*dz/T0); require positive temperature along the path. Use the isothermal limit at L=0 and a stable log1p(x)/x evaluation near zero; this avoids cancellation. No universal standard atmosphere claim.

For a liquid with constant isothermal bulk modulus K, d rho/dp=rho/K. Integrating gives rho=rho0*exp((p-p0)/K). In downward coordinate h, dp/dh=rho*g yields delta_p=-K*log1p(-rho0*g*h/K), rho=rho0/(1-rho0*g*h/K). Require 1-rho0*g*h/K>0; approaching this mathematical singularity is outside realistic constant-K material behavior. This is an idealized constitutive model, not an accurate seawater EOS. The existing small-strain model remains separate. Some extracted formulas in older source text appear internally inconsistent (signs, Taylor coefficients or dimensions); derive and verify independently instead of transcribing them. PDF extraction artifacts cannot be distinguished from printed errors without the unavailable page images.

### Hydrostatic loads

For a fully wetted plane in one constant-density liquid, net pressure relative to the opposite side can be written p(s)=p_c+rho*g*sin(theta)*s, with s measured along the plane downhill from its centroid. Then resultant normal force F=A*p_c, centroidal moment M=rho*g*sin(theta)*I_c, and line-of-action offset s_cp=M/F. Keep signed moment and force even when F=0; center of pressure then undefined (a nonzero pure couple may remain). Uniform opposing pressure shifts F and center of pressure, not the gradient moment. General nonsymmetric shapes need both in-plane centroidal moments/products of inertia. Partial immersion and multiple layers require clipping or explicit integration; do not use the single-layer formula over dry area.

Curved loads follow F=-integral(p*n dA), for normals outward from the loaded solid. Horizontal projections and signed liquid-column weights are special reductions for suitable geometry; use vector quadrature and moment accumulation for general curves. Do not add atmospheric pressure twice or assume all vertical forces point down. For a closed wetted surface under uniform pressure, resultant and torque vanish.

### Buoyancy and stability

Integrating pressure over a submerged closed body gives upward rho*g*V for a homogeneous fluid. In layers, use g*sum(rho_i*V_i) and a density-weighted centroid for the buoyancy line of action. For an object floating freely at the surface of a single liquid, displaced mass equals body mass if gas buoyancy is negligible; a ratio greater than one is not a valid floating state. Initial stability of a conventional floating body uses GM=KB+I_waterplane/V_displaced-KG, consistent vertical datum and heel axis. Positive GM indicates local small-angle stability, not large-angle or regulatory stability. A fully submerged body has different stability criteria (relative G/B positions); never apply floating waterplane formula to it.

### Rigid-body acceleration and rotation

For a translating tank accelerating with constant vector a, grad(p)=rho*(g_vector-a). Use dot product with position difference. Free surface is an equipotential; if effective gravity is zero, the usual planar free-surface direction is undefined. For steady rigid rotation about a vertical axis, dp/dr=rho*omega^2*r and dp/dz=-rho*g; z(r)-z(0)=omega^2*r^2/(2*g) on the free surface. Calculate level difference using (r2-r1)*(r2+r1) when close radii could cause cancellation. Volume conservation must be checked independently when a tank spills or exposes its floor. No transient sloshing model.

## Integral balances and follow-on design

Use outward normal n and relative boundary velocity u-u_boundary in mass flux. Momentum flux transports absolute velocity u, multiplied by relative normal flux; do not use the same scalar speed for both in a moving control volume. Pressure force on fluid is -p*n*A, support force on hardware is opposite wall-on-fluid force. For steady nonuniform profiles, compute momentum and kinetic energy correction factors separately. For fully developed laminar circular velocity u=2U*(1-(r/R)^2), independent integration gives beta=4/3 and alpha=2. For signed/reversing or multidirectional profiles use integral fluxes, not these scalar correction factors.

For steady incompressible mechanical energy, use H=z+p/(rho*g)+alpha*U^2/(2*g). The balance is H1+h_p-h_t-h_loss=H2. Keep ideal Bernoulli distinct from this model. Darcy loss h_f=f_D*(L/D)*U^2/(2*g), with f_D=4*f_F; for a signed pressure-loss relation use U*abs(U). Zero-flow pressure drop is zero even though the laminar friction factor itself diverges as Re approaches zero. No numerical root is needed for known laminar pressure drop. Colebrook original paper and calibration ranges remain pending; compare implicit and explicit correlations only after source verification.

Liburdy's boundary-layer material motivates separating exact pointwise analytic profiles from numerical integration of the boundary-layer equations. Panel methods represent inviscid pressure forces and do not directly predict viscous drag. Treat those as future distinct model families, with independent verification rather than extending scalar formulas indiscriminately.

## Sandbox mathematical cross-check (actual execution)

Python with SciPy quadrature and solve_ivp; inputs below are independently selected synthetic examples, not reproduced textbook exercises. This validates formulas under their assumptions, not real-fluid accuracy.

| Case | Analytical | Independent comparison |
|---|---:|---:|
| Constant-K liquid, rho0=1000 kg/m^3, g=9.81, K=2.2 GPa, h=10 km | delta_p=100354458.11704043 Pa | direct ODE integration 100354458.11703426 Pa; relative difference 6.15e-14; incompressible approximation 98100000 Pa |
| Isothermal ideal gas, p0=101325 Pa, R=287.05, T=293.15 K, dz=4 km | 63562.0026818 Pa | constant-density approximation 54075.3972655 Pa (not an exact reference; illustrates model-choice effect) |
| Fully submerged rectangle b=2 m, L=3 m, theta=30 deg, centroid depth=2 m, external net surface pressure=10 kPa, rho=1000, g=9.81 | F=177720 N, offset 0.124198176907495 m | quadrature of pressure and moment gave 177720 N and 0.124198176907495 m |
| Rigid rotation omega=4 rad/s, radius=2 m, g=9.81 | rim-center elevation=3.26197757390418 m | analytical sanity value; not an independent numerical test |

No calculator code was changed in this research commit. Next implementation should consume these derived formulas and add shared Python/JS fixtures, dimensional/limit checks and browser tests. Remaining topics FM03–FM15 retain their previous coverage/review status until substantive sections are actually inspected. This log deliberately does not assert all books have been read.
