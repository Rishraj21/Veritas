"""Optional partial symmetric eigenpairs with residual and orthogonality checks."""
from dataclasses import dataclass
from .hybrid import _backend, _operator
from ._validation import count, positive

@dataclass(frozen=True, slots=True)
class EigenResult:
    values: object
    vectors: object
    relative_residuals: object
    orthogonality_error: float
    converged: bool


def partial_eigenpairs(a, k, *, ncv=None, which='SA', tol=1e-9, max_iter=2000,
                       basis_budget_bytes=None):
    """Caller guarantees a real symmetric fixed operator. ARPACK Lanczos.

    Budget counts the Lanczos basis payload only. Residuals are scaled by
    max(1, |lambda|, ||Av||); they do not certify completeness of the spectrum.
    """
    np, _, sl = _backend()
    a = _operator(a); n = a.shape[0]; k = count(k, 'k')
    if k >= n or which not in ('SA', 'LA', 'SM', 'LM'):
        raise ValueError('Require k < n and a supported spectrum selector')
    tol = positive(tol, 'tol'); max_iter = count(max_iter, 'max_iter')
    m = min(n, max(2*k+1, 20)) if ncv is None else count(ncv, 'ncv')
    if basis_budget_bytes is not None:
        m = min(m, count(basis_budget_bytes, 'basis_budget_bytes')//(8*n))
    if not k < m <= n:
        raise ValueError('Lanczos basis must fit k < ncv <= n and budget')
    # Force double precision even for a float32 input operator.
    op = sl.LinearOperator(a.shape, matvec=lambda v: np.asarray(a.matvec(v), dtype=np.float64), dtype=np.float64)
    complete = True
    try:
        vals, vecs = sl.eigsh(op, k=k, which=which, ncv=m, tol=tol, maxiter=max_iter)
    except sl.ArpackNoConvergence as exc:
        vals, vecs, complete = exc.eigenvalues, exc.eigenvectors, False
    order = np.argsort(vals); vals, vecs = vals[order], vecs[:, order]
    residuals = np.empty(len(vals))
    for j, v in enumerate(vals):
        av = op.matvec(vecs[:,j]); residuals[j] = np.linalg.norm(av-v*vecs[:,j])/max(1.,abs(v),np.linalg.norm(av))
    orth = float(np.linalg.norm(vecs.T@vecs-np.eye(len(vals)), ord='fro'))
    ok = complete and len(vals)==k and bool(np.all(residuals <= 10*tol)) and orth <= max(10*tol, 1e-12)*k
    return EigenResult(vals, vecs, residuals, orth, ok)
