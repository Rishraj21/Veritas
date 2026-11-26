# Phase 0 — Numerical methods

Scope reference: T. A. Driscoll and R. J. Braun, Fundamentals of Numerical Computation (online undergraduate textbook), https://tobydriscoll.net/book/fnc/index.html ; chapters on nonlinear equations, interpolation, finite differences, quadrature, linear systems and differential equations. Also J. F. Epperson, An Introduction to Numerical Methods and Analysis, 3rd ed., chapters 3–6 and 8–9 (publisher contents). These are curriculum references; no claim of exhaustive chapter review. The implementation is original and independent of textbook code.

| ID | Family | API or planned scope | Status |
|---|---|---|---|
| NM01 | Scalar roots | bisection, newton, secant | Implemented; CI passed at 5fe413c |
| NM02 | Quadrature | trapezoidal, midpoint, simpson, simpson38 | Implemented; CI passed at 5fe413c |
| NM03 | Differentiation | derivative (forward/backward/central), second_derivative | Implemented; CI passed at 5fe413c |
| NM04 | Interpolation | one-shot and reusable linear/Newton interpolators; spline pending | Partial; CI passed at 1e1d093 |
| NM05 | Linear algebra | lu_factor, solve_linear, residual/backward error, optional infinity condition number; tridiagonal factorization, Jacobi/Gauss-Seidel; general sparse and eigenvalues pending | Partial; CI passed at 1e1d093 |
| NM06 | ODE | solve_ivp: Euler, midpoint RK2, Heun RK2, classical RK4; adaptive and stiff methods pending | Partial; CI passed at b67e284 |
| NM07 | PDE | 1D Poisson and heat equation; explicit, backward Euler, Crank-Nicolson; fixed Dirichlet boundaries | Partial; local tests passed, hosted CI pending |
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

- LU: factor a square real matrix as P A = L U, choosing pivots by |a_ik|/s_i, where s_i is the largest absolute entry of the original row. Reuse factors to solve multiple right-hand sides via triangular substitution. A default relative pivot threshold rejects numerically small pivots; a rejection is not proof of exact singularity. No general sparse systems, QR, SVD, eigenvalue algorithms or least squares yet.
- Linear diagnostics: r = b-Ax, residual infinity norm, normwise backward error ||r||inf/(||A||inf ||x||inf + ||b||inf), optional infinity condition number ||A||inf ||A^-1||inf via n solves. A small residual alone does not guarantee a small forward error. Diagnostics are floating-point estimates and extreme scales may overflow; use a robust backend for production.
- IVP y'=f(t,y): Euler uses k1=f(t,y), y_next=y+h*k1. Midpoint uses k2=f(t+h/2,y+h*k1/2) and y_next=y+h*k2; Heun averages start and predicted end slopes. Classical RK4 uses two midpoint slopes and one end slope with weights 1/6, 1/3, 1/3, 1/6. Global orders 1, 2, 2 and 4 under appropriate smoothness and stability assumptions. No adaptive tolerances, event handling, stiffness support or certified error bounds. Supports scalar and vector state, forward/reverse time and exact final time.
- Absolute stability polynomial R(z)=sum(z^j/j!,j=0..p) for these methods, p=1,2,2,4. The criterion |R(z)|<=1 applies to the scalar linear test equation; it is not a guarantee of nonlinear or nonnormal-system stability.
- Error norms: L1=sum(|e|), L2=sqrt(sum(e^2)), Linf=max(|e|), MAE=L1/n, RMSE=L2/sqrt(n), relative L2=L2/||reference||2 (undefined for zero reference). Samples must be paired and unit-compatible; these are not volume-weighted field norms.

Tests: tests/test_math_linear_ode.py covers pivoted factor reconstruction, reuse, conditioning, singularity, order under step refinement, vector oscillator, reversed time, stability and invalid inputs. Reproduce examples using python examples/numerical_foundation.py. CI passed at b67e284.

## Efficiency review

- Quadrature streams weighted samples into math.fsum rather than materializing lists. Linear work, no sample-sized temporary array (fsum maintains floating-point partial sums).
- LU factors remain packed; condition diagnostics accumulate inverse row sums one column at a time with compensated addition. O(n) auxiliary storage beyond factors, rather than O(n^2) inverse columns; time remains O(n^3).
- Error norms consume paired iterators in one pass with constant auxiliary storage, compensated L1 and scaled hypot for L2. No materialized samples; mismatched lengths still rejected.
- Fixed-step ODE integration retains all states by default. store_every=k reduces saved samples to O((n/k+1)*d) for state dimension d, without changing integration steps or accuracy. k>=n retains endpoints only; internal stage storage O(d). No dense output or interpolation promised.

Memory regression checks use tracemalloc with generous absolute limits to detect reintroduced sample-sized arrays. These are not production performance benchmarks. Future changes should report input size, wall time, peak memory, error and convergence, and distinguish theoretical complexity from measurements.

## Structured linear systems and reusable interpolation

Theory references: Barrett et al., [Templates for the Solution of Linear Systems](https://www.netlib.org/templates/), sections 2.2.1 and 2.2.2 (Jacobi and Gauss-Seidel); Driscoll and Braun, [Piecewise linear interpolation](https://fncbook.com/pwlin/). Implementations are original.

For a tridiagonal system with diagonal d, lower l, and upper u, Thomas elimination uses m_i=l_i/d_i and d_(i+1) <- d_(i+1)-m_i*u_i. Apply the same elimination to each RHS, then back-substitute. Requires safe pivots, typically suitable for well-scaled strictly diagonally dominant or SPD systems; no pivoting, no claim of stability for arbitrary matrices. A rejected pivot can occur in a nonsingular matrix. Use pivoted dense LU for small general systems, or a tested pivoted banded backend at larger scale.

Jacobi replaces every component using the previous iterate. Gauss-Seidel uses updated components immediately. Strict diagonal dominance is sufficient for both to converge; arbitrary tridiagonal shape is not. Both use the true residual infinity norm, with tolerance atol + rtol*||b||inf; convergence does not certify forward accuracy for ill-conditioned systems. Finite nonconvergence returns a status; overflow or invalid input raises an error. Gauss-Seidel needs no second iterate buffer. These methods are useful as educational smoothers; not recommended as a default for general large sparse systems. CG, Krylov methods and multigrid require separate study.

| Method | Setup/work | Per RHS or sweep | Matrix/factor storage |
|---|---|---|---|
| Dense pivoted LU | O(n^3) | O(n^2) | O(n^2) |
| Thomas (tridiagonal) | O(n) | O(n) | O(n) |
| Jacobi (tridiagonal) | O(n) | O(n) per sweep | O(n) |
| Gauss-Seidel (tridiagonal) | O(n) | O(n) per sweep | O(n) |

A reusable linear interpolator validates and snapshots the nodes once, then uses binary search for O(log n) queries with constant auxiliary space. A reusable Newton interpolator precomputes O(n^2) divided differences once with O(n) storage, then uses nested evaluation in O(n) per query. High-degree interpolation can be ill-conditioned even with exact coefficients; local linear interpolation is often safer for tabulated physical properties. No extrapolation is implicit.

Tests compare banded solutions with pivoted dense LU and known solutions, exercise invalid pivots and nonconvergence, check a 10,000-unknown memory regression, and verify interpolation exactness and reusable data snapshots. Run python examples/structured_solvers.py for measured timings, traced peak Python allocations and residuals. The dense path includes dense construction; the structured paths reuse a previously constructed banded matrix; measurements are not equivalent end-to-end timings and do not include native allocations. The primary benefit is structural complexity reduction, not a guaranteed speedup on all problems.

## Finite-difference PDE foundation

For -u''=f, the interior stencil is -u_(i-1)+2u_i-u_(i+1)=dx^2*f_i. Constant prescribed endpoint values enter the right-hand side. For u_t=alpha*u_xx, the theta method combines the old-time Laplacian with weight 1-theta and new-time Laplacian with weight theta. theta=0 is FTCS, theta=1 backward Euler, theta=1/2 Crank-Nicolson. The latter two reuse a single Thomas factorization. On the uniform grid the diffusion number is r=alpha*dt/dx^2; FTCS enforces r<=1/2. The implicit methods are linearly stable for this diffusion model, but large r can impair accuracy and Crank-Nicolson can oscillate. Smooth compatible data yield second-order spatial truncation; time truncation is first order for FTCS/backward Euler and second order for Crank-Nicolson.

Theory reference: Driscoll and Braun, Fundamentals of Numerical Computation, chapter on diffusion equations (https://fncbook.com/). Original implementation. Work O(N) for Poisson and O(N*T) for T diffusion steps; O(N) working storage plus retained output O(N*(1+ceil(T/k))) for store_every=k. Fixed Dirichlet only, constant diffusivity, no source in transient model, uniform grid, real scalars, no error controller. The initial callable is sampled only on interior nodes; compatibility with imposed boundary values is the caller's responsibility. Neumann/Robin, multidimensional and variable-coefficient models remain pending.

Local tests: 13 existing structured-solver/interpolation tests and 10 new PDE tests passed in a reconstructed local subset; the four source dependency blobs and existing test blob matched the GitHub snapshot. Full previous CI passed. New tests cover a quadratic exact solution, second-order spatial refinement, sine decay, nonzero fixed boundary conditions, output retention and invalid stability settings. Hosted CI for this commit remains to be checked.

Local allocation comparison: 500 cells, 200 steps, Crank-Nicolson, initial sin(pi*x), diffusivity 0.1, duration 0.1. Full retention: 201 states, 3306332 peak traced bytes, 0.625 s; endpoints only: 2 states, 118640 peak traced bytes, 0.593 s. Both final maximum absolute errors against the analytic solution were 2.923662462e-7. Single runs under tracemalloc; not general performance claims. Reproduce with python examples/diffusion_memory.py.
