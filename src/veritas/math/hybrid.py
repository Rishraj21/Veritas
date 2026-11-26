"""Optional compiled sparse and matrix-free solvers; float64 by default."""
from dataclasses import dataclass
from functools import lru_cache
from ._validation import count, finite


def _backend():
    try:
        import numpy as np
        import scipy.sparse as sp
        import scipy.sparse.linalg as sl
    except ImportError as exc:
        raise ImportError("Install veritas-eng[accelerated] for this backend") from exc
    return np, sp, sl


def _operator(a):
    np, sp, sl = _backend()
    if not (sp.issparse(a) or isinstance(a, sl.LinearOperator)):
        raise TypeError("Expected a SciPy sparse matrix or LinearOperator")
    if a.shape[0] != a.shape[1] or not a.shape[0]:
        raise ValueError("Expected a nonempty square operator")
    if a.dtype is None or a.dtype.kind not in 'fiub':
        raise ValueError("Expected a real operator with declared dtype")
    return sl.aslinearoperator(a)


@dataclass(frozen=True, slots=True)
class HybridResult:
    solution: object
    residual_l2: float
    converged: bool
    methods: tuple
    info: int


def solve_sparse(a, b, *, spd=False, rtol=1e-8, atol=0., max_iter=1000,
                 restart=30, basis_budget_bytes=None):
    """CG for caller-declared SPD; otherwise BiCGSTAB then restarted GMRES.

    The budget caps only GMRES's float64 Krylov basis, not total process RAM.
    Each attempted method has its own iteration limit. No matrix densification.
    Independently recompute residual; no convergence claim from status alone.
    """
    np, _, sl = _backend()
    a = _operator(a); n = a.shape[0]
    b = np.asarray(b)
    if b.dtype.kind not in 'fiub' or b.shape != (n,):
        raise ValueError("Expected a real RHS vector matching the operator")
    b = np.asarray(b, dtype=np.float64)
    if not np.all(np.isfinite(b)):
        raise ValueError("Nonfinite RHS")
    rtol, atol = finite(rtol, 'rtol'), finite(atol, 'atol')
    if min(rtol, atol) < 0 or not (rtol or atol):
        raise ValueError("Require nonnegative tolerances, at least one positive")
    max_iter = count(max_iter, 'max_iter'); restart = min(n, count(restart, 'restart'))
    if basis_budget_bytes is not None:
        budget = count(basis_budget_bytes, 'basis_budget_bytes')
        restart = min(restart, max(0, budget//(8*n)-1))
    target = finite(max(atol, rtol*float(np.linalg.norm(b))), 'residual tolerance')
    methods = []
    for method in (('cg',) if spd else ('bicgstab', 'gmres')):
        if method == 'gmres' and restart < 1:
            break
        methods.append(method)
        kw = dict(rtol=rtol, atol=atol, maxiter=max_iter)
        if method == 'gmres':
            kw.update(restart=restart, callback=lambda _: None, callback_type='legacy')
        x, info = getattr(sl, method)(a, b, **kw)
        residual = float(np.linalg.norm(b-a.matvec(x)))
        ok = info == 0 and np.isfinite(residual) and residual <= target
        if ok:
            return HybridResult(x, residual, True, tuple(methods), int(info))
    return HybridResult(x, residual, False, tuple(methods), int(info))


def _stencil(x, out, nx, ny):
    for j in range(ny):
        for i in range(nx):
            k = j*nx+i
            out[k] = (4*x[k] - (x[k-1] if i else 0.)
                      - (x[k+1] if i+1<nx else 0.)
                      - (x[k-nx] if j else 0.)
                      - (x[k+nx] if j+1<ny else 0.))


@lru_cache(maxsize=1)
def _compiled_stencil():
    try:
        from numba import njit
    except ImportError as exc:
        raise ImportError("Install veritas-eng[jit] for compiled stencils") from exc
    return njit(_stencil)


def poisson_operator(nx, ny, *, compiled=False):
    """Unscaled homogeneous Dirichlet five-point Laplacian, no matrix storage."""
    np, _, sl = _backend()
    nx, ny = count(nx, 'nx'), count(ny, 'ny'); n = nx*ny
    kernel = _compiled_stencil() if compiled else _stencil
    def apply(x):
        x = np.asarray(x).reshape(n)
        if x.dtype.kind not in 'fiub':
            raise ValueError("Expected real vector")
        x = np.asarray(x, dtype=np.float64)
        out = np.empty(n, dtype=np.float64)
        kernel(x, out, nx, ny)
        return out
    return sl.LinearOperator((n,n), matvec=apply, rmatvec=apply, dtype=np.float64)
