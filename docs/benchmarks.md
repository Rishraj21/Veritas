# Benchmark reference notes

These closed-form relations are standard textbook solutions, implemented here independently. No textbook content or numerical datasets are redistributed. Suggested references for independent review:

- Fluid mechanics: Frank M. White, *Fluid Mechanics* — fully developed viscous internal flows (circular tubes and parallel plates).
- Mechanics of materials: Gere and Goodno, *Mechanics of Materials* — axial deformation, torsion and beam deflection.
- Heat transfer: Incropera et al., *Fundamentals of Heat and Mass Transfer* — plane walls, extended surfaces, transient lumped systems.
- Vibrations: S. S. Rao, *Mechanical Vibrations* — undamped single-degree-of-freedom free vibration.
- Grid convergence: P. J. Roache, *Verification and Validation in Computational Science and Engineering* — Richardson extrapolation and observed order.

These references are suggested review sources, not independently inspected edition/page citations. Contributors should supply a precise, accessible reference when proposing benchmark additions. The current tests exercise hand-evaluable reference values and synthetic observed outputs; no external solver has been executed or independently benchmarked in this release.

All lengths are metres, forces newtons, pressures pascals, absolute temperatures kelvin, and frequencies hertz unless the catalogue states otherwise. Physical assumptions (for example laminar flow, small deflection, or Biot number) must be confirmed by the user; required regime parameters are not currently provided for automatic verification.
