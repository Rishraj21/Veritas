"""Packed, matrix-free preconditioned conjugate gradients for real SPD systems."""
from array import array
from dataclasses import dataclass
from math import fsum, sqrt, isfinite
from ._validation import finite, count


@dataclass(frozen=True, slots=True)
class CGResult:
    """Solution is a read-only view of an owned packed double buffer."""
    solution: memoryview
    residual_l2: float
    iterations: int
    matvecs: int
    converged: bool
    reason: str


def _packed(values):
    return array('d', (finite(v, 'vector entry') for v in values))


def _norm(v):
    scale = max(map(abs, v), default=0.)
    return finite(scale*sqrt(fsum((x/scale)**2 for x in v)), 'norm') if scale else 0.


def conjugate_gradient(matvec, b, *, x0=None, diagonal=None, rtol=1e-8,
                       atol=0., max_iter=None):
    """Solve A x=b for a symmetric positive definite operator A.

    matvec(readonly_x, writable_out) must overwrite every entry, not retain
    either view, and represent a fixed linear operator. Optional positive
    diagonal supplies a Jacobi preconditioner. True residual is checked
    before success and on termination. No matrix or iteration history stored.
    SPD is a caller assumption, not established by curvature checks.
    """
    b = _packed(b); n = len(b)
    if not n: raise ValueError('Empty right-hand side')
    max_iter = count(max_iter if max_iter is not None else 10*n, 'max_iter')
    rtol, atol = finite(rtol, 'rtol'), finite(atol, 'atol')
    if min(rtol, atol) < 0 or not (rtol or atol):
        raise ValueError('Require nonnegative tolerances, at least one positive')
    x = _packed(x0) if x0 is not None else array('d', [0.])*n
    if len(x) != n: raise ValueError('Initial vector length mismatch')
    d = _packed(diagonal) if diagonal is not None else None
    if d is not None and (len(d) != n or any(v <= 0 for v in d)):
        raise ValueError('Preconditioner diagonal must be positive and match b')
    r = array('d', [0.])*n; p = array('d', [0.])*n; q = array('d', [0.])*n
    xv, pv, qv = memoryview(x).toreadonly(), memoryview(p).toreadonly(), memoryview(q)
    calls = 0
    tol = finite(max(atol, rtol*_norm(b)), 'residual tolerance')
    def apply(v):
        nonlocal calls
        for i in range(n): q[i] = float('nan')
        matvec(v, qv)
        calls += 1
        if not all(map(isfinite, q)):
            raise ValueError('Operator must overwrite all entries with finite values')
    def refresh():
        apply(xv)
        for i in range(n): r[i] = finite(b[i]-q[i], 'true residual')
        return _norm(r)
    def start():
        for i in range(n): p[i] = finite(r[i]/d[i] if d is not None else r[i], 'direction')
        return finite(fsum(a*z for a,z in zip(r,p)), 'residual product')
    def finish(k, reason):
        residual = refresh()
        ok = residual <= tol
        return CGResult(xv, residual, k, calls, ok, 'residual tolerance' if ok else reason)
    if x0 is None:
        r[:] = b
    else:
        refresh()
    if _norm(r) <= tol: return finish(0, 'initial residual')
    rho = start()
    for k in range(1, max_iter+1):
        if rho <= 0: return finish(k-1, 'residual product breakdown')
        apply(pv)
        curvature = finite(fsum(a*z for a,z in zip(p,q)), 'curvature')
        if curvature <= 0: return finish(k-1, 'nonpositive curvature')
        alpha = finite(rho/curvature, 'step')
        for i in range(n):
            x[i] = finite(x[i]+alpha*p[i], 'iterate')
            r[i] = finite(r[i]-alpha*q[i], 'residual')
        if _norm(r) <= tol:
            residual = refresh()
            if residual <= tol:
                return CGResult(xv, residual, k, calls, True, 'residual tolerance')
            # Recursive residual drift: restart from the actual residual.
            rho = start()
            continue
        # q is dead after the residual update; use it as the preconditioned
        # residual buffer rather than allocating an additional full vector.
        for i in range(n): q[i] = finite(r[i]/d[i] if d is not None else r[i], 'preconditioned residual')
        newrho = finite(fsum(a*z for a,z in zip(r,q)), 'residual product')
        if newrho <= 0: return finish(k, 'residual product breakdown')
        beta = finite(newrho/rho, 'direction weight')
        for i in range(n): p[i] = finite(q[i]+beta*p[i], 'direction')
        rho = newrho
    return finish(max_iter, 'iteration limit')


@dataclass(frozen=True, slots=True)
class PoissonStencil2D:
    """Unscaled five-point negative Laplacian, zero Dirichlet boundaries.

    nx, ny are interior unknown counts, equal grid spacing in both axes.
    Multiply the physical RHS by h**2 before solving. No assembled matrix.
    """
    nx: int
    ny: int

    def __post_init__(self):
        count(self.nx, 'nx'); count(self.ny, 'ny')

    def __call__(self, x, out):
        nx, ny = self.nx, self.ny
        n = nx*ny
        if len(x) != n or len(out) != n: raise ValueError('Stencil vector length mismatch')
        for j in range(ny):
            for i in range(nx):
                k = j*nx+i
                out[k] = (4*x[k] - (x[k-1] if i else 0.)
                          - (x[k+1] if i+1<nx else 0.)
                          - (x[k-nx] if j else 0.)
                          - (x[k+nx] if j+1<ny else 0.))
