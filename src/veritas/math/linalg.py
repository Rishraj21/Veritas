"""Small dense real linear systems via scaled partial-pivoted LU.

Educational O(n^3) factorization; no sparse or production-scale backend.
"""
from dataclasses import dataclass
from math import fsum
from ._validation import finite

def _vector(values,n=None):
    v=tuple(finite(x,"vector entry") for x in values)
    if not v or (n is not None and len(v)!=n):
        raise ValueError("Vector length mismatch")
    return v

def _matrix(matrix):
    a=tuple(_vector(row) for row in matrix)
    if not a or any(len(row)!=len(a) for row in a):
        raise ValueError("Expected a nonempty square matrix")
    return a

def _norminf(a):
    return finite(max(fsum(abs(x) for x in row) for row in a),"matrix norm")

@dataclass(frozen=True)
class LUFactor:
    """Compact factors satisfying A[permutation,:] = L U."""
    packed: tuple
    permutation: tuple
    swaps: int

    def solve(self,b):
        n=len(self.packed)
        b=_vector(b,n)
        y=[0.0]*n
        for i,row in enumerate(self.packed):
            y[i]=finite(b[self.permutation[i]]-fsum(row[j]*y[j] for j in range(i)),"forward substitution")
        x=[0.0]*n
        for i in range(n-1,-1,-1):
            row=self.packed[i]
            x[i]=finite((y[i]-fsum(row[j]*x[j] for j in range(i+1,n)))/row[i],"back substitution")
        return tuple(x)

    def unpack(self):
        n=len(self.packed)
        l=tuple(tuple(self.packed[i][j] if i>j else float(i==j) for j in range(n)) for i in range(n))
        u=tuple(tuple(self.packed[i][j] if i<=j else 0.0 for j in range(n)) for i in range(n))
        return l,u

def lu_factor(matrix,*,pivot_tol=1e-14):
    """Scaled partial pivoting; reject pivots at or below pivot_tol*row_scale.

    The tolerance is a numerical policy, not a mathematical singularity proof.
    Set pivot_tol=0 to reject only exact zero pivots.
    """
    a=[list(row) for row in _matrix(matrix)]
    tol=finite(pivot_tol,"pivot_tol")
    if not 0<=tol<1:
        raise ValueError("pivot_tol must be in [0,1)")
    n=len(a)
    scales=[max(map(abs,row)) for row in a]
    if any(s==0 for s in scales):
        raise ValueError("Singular matrix: zero row")
    perm=list(range(n)); swaps=0
    for k in range(n):
        p=max(range(k,n),key=lambda i:abs(a[i][k])/scales[i])
        if abs(a[p][k])/scales[p]<=tol:
            raise ValueError("Zero or numerically small pivot")
        if p!=k:
            a[k],a[p]=a[p],a[k]
            scales[k],scales[p]=scales[p],scales[k]
            perm[k],perm[p]=perm[p],perm[k]
            swaps+=1
        for i in range(k+1,n):
            a[i][k]=finite(a[i][k]/a[k][k],"LU multiplier")
            for j in range(k+1,n):
                a[i][j]=finite(a[i][j]-a[i][k]*a[k][j],"LU entry")
    return LUFactor(tuple(map(tuple,a)),tuple(perm),swaps)

@dataclass(frozen=True)
class LinearResult:
    solution: tuple
    residual_inf: float
    backward_error: float
    condition_inf: float | None

def solve_linear(matrix,b,*,pivot_tol=1e-14,condition=False):
    """Solve Ax=b; report infinity residual and normwise backward error.

    condition=True computes ||A||inf*||A^-1||inf using n triangular solves.
    This floating-point diagnostic is not a certified forward-error bound.
    """
    a=_matrix(matrix); b=_vector(b,len(a))
    factor=lu_factor(a,pivot_tol=pivot_tol)
    x=factor.solve(b)
    r=max(abs(finite(bi-fsum(ai*xj for ai,xj in zip(row,x)),"residual")) for row,bi in zip(a,b))
    an=_norminf(a); xn=max(map(abs,x)); bn=max(map(abs,b))
    denominator=finite(an*xn+bn,"backward error denominator")
    eta=r/denominator if denominator else 0.0
    kappa=None
    if condition:
        n=len(a)
        # Accumulate inverse row sums one column at a time; no inverse storage.
        # Compensated sums limit rounding accumulation over many columns.
        sums=[0.0]*n
        corrections=[0.0]*n
        for j in range(n):
            col=factor.solve(float(i==j) for i in range(n))
            for i,v in enumerate(col):
                term=abs(v)-corrections[i]
                updated=finite(sums[i]+term,"inverse row sum")
                corrections[i]=(updated-sums[i])-term
                sums[i]=updated
        invnorm=max(sums)
        kappa=finite(an*invnorm,"condition number")
    return LinearResult(x,r,eta,kappa)
