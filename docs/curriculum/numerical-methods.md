# Phase 0 — Numerical methods

Scope reference: T. A. Driscoll and R. J. Braun, Fundamentals of Numerical Computation (online undergraduate textbook), https://tobydriscoll.net/book/fnc/index.html ; chapters on nonlinear equations, interpolation, finite differences, quadrature, linear systems and differential equations. Also J. F. Epperson, An Introduction to Numerical Methods and Analysis, 3rd ed., chapters 3–6 and 8–9 (publisher contents). These are curriculum references; no claim of exhaustive chapter review. The implementation is original and independent of textbook code.

| ID | Family | API or planned scope | Status |
|---|---|---|---|
| NM01 | Scalar roots | bisection, newton, secant | Implemented; CI passed at 5fe413c |
| NM02 | Quadrature | trapezoidal, midpoint, simpson, simpson38 | Implemented; CI passed at 5fe413c |
| NM03 | Differentiation | derivative (forward/backward/central), second_derivative | Implemented; CI passed at 5fe413c |
| NM04 | Interpolation | linear_interpolate, newton_interpolate | Implemented; CI passed at 5fe413c |
| NM05 | Linear algebra | lu_factor, solve_linear, residual/backward error, optional infinity condition number; eigenvalues pending | Partial; new CI required |
| NM06 | ODE | solve_ivp: Euler, midpoint RK2, Heun RK2, classical RK4; adaptive and stiff methods pending | Partial; new CI required |
| NM07 | PDE | FDM/FVM prototypes, stability, manufactured solutions | Planned |
| NM08 | Numerical error | observed convergence, error norms, roundoff, uncertainty | Discrete error norms and scalar ODE stability added; existing three-grid convergence; uncertainty pending |
| NM09 | Optimization | bounded scalar minimization, constrained optimization interfaces | Planned |
| NM10 | Shared infrastructure | SI conversion, validation, result metadata, property provenance | Partial |

## Implemented formulas and assumptions

- Bisection: midpoint of a sign-changing bracket; continuity is required. Halve the bracket until both width and residual criteria are satisfied, or report failure. Newton: x_next = x - f(x)/f'(x); local convergence only. Secant: x_next = x - f(x)(x-x_prev)/(f(x)-f(x_prev)); local convergence only. All return RootResult with absolute residual, iteration count, convergence flag and reason. Exact floating-point zero is not proof of mathematical exactness.
- Composite quadrature: uniform n-panel spacing h=(b-a)/n. Trapezoid weights [1/2,1,...,1,1/2] times h; midpoint weights 1 at panel centers times h; Simpson 1/3 weights [1,4,2,...,4,1] times h/3 (even n); Simpson 3/8 weights [1,3,3,2,...,3,3,1] times 3h/8 (n divisible by 3). Smooth integrands, no singular endpoint support. No certified error estimate.
- First derivatives: forward and backward one-sided differences, or central secant across x±h. Second derivative: difference of the adjacent first divided differences times 2/(h_plus+h_minus). Finite step size trades truncation error against cancellation/roundoff. No automatic step selection.
- Linear interpolation: convex weighted average of adjacent data. Newton polynomial: divided differences and nested evaluation; small well-scaled node sets only. No extrapolation; duplicate/unsorted nodes rejected.

Numerical methods use finite real inputs (complex scalar z is accepted for the stability polynomial); caller manages consistent physical units. Tests in tests/test_math_foundation.py use independent polynomials, known roots, convergence ratios, invalid inputs and failure cases. Not substitutes for validated production libraries.

## Linear algebra, initial-value problems and error diagnostics

Theory references: Driscoll and Braun, Fundamentals of Numerical Computation, sections 2.4 [LU factorization](https://tobydriscoll.net/fnc-julia/linsys/lu.html), 2.6 [Row pivoting](https://tobydriscoll.net/fnc-julia/linsys/pivoting.html), 2.8 [Conditioning of linear systems](https://fncbook.com/julia/condition-number/), 6.2 [Euler's method](https://tobydriscoll.net/fnc-julia/ivp/euler.html), 6.4 [Runge–Kutta methods](https://tobydriscoll.net/fnc-julia/ivp/rk.html) and 11.3 [Absolute stability](https://tobydriscoll.net/fnc-julia/diffusion/absstab-diffusion.html). Original implementation; references provide theory, not copied textbook code.

- LU: factor a square real matrix as P A = L U, choosing pivots by |a_ik|/s_i, where s_i is the largest absolute entry of the original row. Reuse factors to solve multiple right-hand sides via triangular substitution. A default relative pivot threshold rejects numerically small pivots; a rejection is not proof of exact singularity. No large sparse systems, QR, SVD, eigenvalue algorithms or least squares in this batch.
- Linear diagnostics: r = b-Ax, residual infinity norm, normwise backward error ||r||inf/(||A||inf ||x||inf + ||b||inf), optional infinity condition number ||A||inf ||A^-1||inf via n solves. A small residual alone does not guarantee a small forward error. Diagnostics are floating-point estimates and extreme scales may overflow; use a robust backend for production.
- IVP y'=f(t,y): Euler uses k1=f(t,y), y_next=y+h*k1. Midpoint uses k2=f(t+h/2,y+h*k1/2) and y_next=y+h*k2; Heun averages start and predicted end slopes. Classical RK4 uses two midpoint slopes and one end slope with weights 1/6, 1/3, 1/3, 1/6. Global orders 1, 2, 2 and 4 under appropriate smoothness and stability assumptions. No adaptive tolerances, event handling, stiffness support or certified error bounds. Supports scalar and vector state, forward/reverse time and exact final time.
- Absolute stability polynomial R(z)=sum(z^j/j!,j=0..p) for these methods, p=1,2,2,4. The criterion |R(z)|<=1 applies to the scalar linear test equation; it is not a guarantee of nonlinear or nonnormal-system stability.
- Error norms: L1=sum(|e|), L2=sqrt(sum(e^2)), Linf=max(|e|), MAE=L1/n, RMSE=L2/sqrt(n), relative L2=L2/||reference||2 (undefined for zero reference). Samples must be paired and unit-compatible; these are not volume-weighted field norms.

Tests: tests/test_math_linear_ode.py covers pivoted factor reconstruction, reuse, conditioning, singularity, order under step refinement, vector oscillator, reversed time, stability and invalid inputs. Reproduce examples using python examples/numerical_foundation.py. New tests are awaiting CI at the time of this commit.
