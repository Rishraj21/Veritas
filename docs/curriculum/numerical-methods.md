# Phase 0 — Numerical methods

Scope reference: T. A. Driscoll and R. J. Braun, Fundamentals of Numerical Computation (online undergraduate textbook), https://tobydriscoll.net/book/fnc/index.html ; chapters on nonlinear equations, interpolation, finite differences, quadrature, linear systems and differential equations. Also J. F. Epperson, An Introduction to Numerical Methods and Analysis, 3rd ed., chapters 3–6 and 8–9 (publisher contents). These are curriculum references; no claim of exhaustive chapter review. The implementation is original and independent of textbook code.

| ID | Family | API or planned scope | Status |
|---|---|---|---|
| NM01 | Scalar roots | bisection, newton, secant | Implemented; CI required |
| NM02 | Quadrature | trapezoidal, midpoint, simpson, simpson38 | Implemented; CI required |
| NM03 | Differentiation | derivative (forward/backward/central), second_derivative | Implemented; CI required |
| NM04 | Interpolation | linear_interpolate, newton_interpolate | Implemented; CI required |
| NM05 | Linear algebra | pivoted linear solve, residuals, matrix conditioning, eigenvalues | Planned |
| NM06 | ODE | Euler, RK2, RK4, adaptive stepping, stiff methods via backend | Planned |
| NM07 | PDE | FDM/FVM prototypes, stability, manufactured solutions | Planned |
| NM08 | Numerical error | observed convergence, error norms, roundoff, uncertainty | Existing limited convergence API; expansion planned |
| NM09 | Optimization | bounded scalar minimization, constrained optimization interfaces | Planned |
| NM10 | Shared infrastructure | SI conversion, validation, result metadata, property provenance | Partial |

## Implemented formulas and assumptions

- Bisection: midpoint of a sign-changing bracket; continuity is required. Halve the bracket until both width and residual criteria are satisfied, or report failure. Newton: x_next = x - f(x)/f'(x); local convergence only. Secant: x_next = x - f(x)(x-x_prev)/(f(x)-f(x_prev)); local convergence only. All return RootResult with absolute residual, iteration count, convergence flag and reason. Exact floating-point zero is not proof of mathematical exactness.
- Composite quadrature: uniform n-panel spacing h=(b-a)/n. Trapezoid weights [1/2,1,...,1,1/2] times h; midpoint weights 1 at panel centers times h; Simpson 1/3 weights [1,4,2,...,4,1] times h/3 (even n); Simpson 3/8 weights [1,3,3,2,...,3,3,1] times 3h/8 (n divisible by 3). Smooth integrands, no singular endpoint support. No certified error estimate.
- First derivatives: forward and backward one-sided differences, or central secant across x±h. Second derivative: difference of the adjacent first divided differences times 2/(h_plus+h_minus). Finite step size trades truncation error against cancellation/roundoff. No automatic step selection.
- Linear interpolation: convex weighted average of adjacent data. Newton polynomial: divided differences and nested evaluation; small well-scaled node sets only. No extrapolation; duplicate/unsorted nodes rejected.

All numerical methods accept finite real scalars; caller manages consistent physical units. Tests in tests/test_math_foundation.py use independent polynomials, known roots, convergence ratios, invalid inputs and failure cases. Not substitutes for validated production libraries.
