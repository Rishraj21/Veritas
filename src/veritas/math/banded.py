"""Tridiagonal linear systems without constructing a dense matrix."""
from dataclasses import dataclass
from math import fsum
from ._validation import finite,count

@dataclass(frozen=True, slots=True, init=False)
class Tridiagonal:
    """Immutable three-band operator; lower and upper have n-1 entries."""
    lower: tuple
    diagonal: tuple
    upper: tuple

    def __init__(self,lower,diagonal,upper):
        d=tuple(finite(x,"diagonal") for x in diagonal)
        l=tuple(finite(x,"lower") for x in lower)
        u=tuple(finite(x,"upper") for x in upper)
        if not d or len(l)!=len(d)-1 or len(u)!=len(d)-1:
            raise ValueError("Expected n diagonal and n-1 off-diagonal entries")
        object.__setattr__(self,"lower",l)
        object.__setattr__(self,"diagonal",d)
        object.__setattr__(self,"upper",u)

    def __len__(self):
        return len(self.diagonal)

    def vector(self,values):
        v=tuple(finite(x,"vector entry") for x in values)
        if len(v)!=len(self):
            raise ValueError("Vector length mismatch")
        return v

    def matvec(self,values):
        x=self.vector(values)
        n=len(self)
        return tuple(finite(fsum((
            self.diagonal[i]*x[i],
            self.lower[i-1]*x[i-1] if i else 0,
            self.upper[i]*x[i+1] if i+1<n else 0
        )),"matrix-vector product") for i in range(n))

    def residual_inf(self,x,b):
        b=self.vector(b)
        return max(abs(finite(v-w,"residual")) for v,w in zip(b,self.matvec(x)))

    def factor(self,*,pivot_tol=1e-14):
        """Thomas elimination; no row pivoting. Reject unsafe small pivots.

        Intended for well-scaled diagonally dominant or suitable SPD systems.
        A rejection is not proof of singularity: use pivoted LU when needed.
        """
        tol=finite(pivot_tol,"pivot_tol")
        if not 0<=tol<1:
            raise ValueError("pivot_tol must be in [0,1)")
        d=list(self.diagonal)
        multipliers=[]
        n=len(self)
        for i in range(n):
            scale=max(abs(self.diagonal[i]),
                      abs(self.lower[i-1]) if i else 0,
                      abs(self.upper[i]) if i+1<n else 0)
            if scale==0 or d[i]==0 or abs(d[i])/scale<=tol:
                raise ValueError("Zero or small Thomas pivot; use a pivoted solver")
            if i+1<n:
                m=finite(self.lower[i]/d[i],"multiplier")
                multipliers.append(m)
                d[i+1]=finite(d[i+1]-m*self.upper[i],"modified diagonal")
        return TridiagonalFactor(tuple(multipliers),tuple(d),self.upper)

@dataclass(frozen=True, slots=True)
class TridiagonalFactor:
    multipliers: tuple
    diagonal: tuple
    upper: tuple

    def solve(self,b):
        """Reuse the factors for a new right-hand side in O(n) time."""
        y=[finite(x,"right-hand side") for x in b]
        n=len(self.diagonal)
        if len(y)!=n:
            raise ValueError("Vector length mismatch")
        for i in range(1,n):
            y[i]=finite(y[i]-self.multipliers[i-1]*y[i-1],"forward substitution")
        y[-1]=finite(y[-1]/self.diagonal[-1],"back substitution")
        for i in range(n-2,-1,-1):
            y[i]=finite((y[i]-self.upper[i]*y[i+1])/self.diagonal[i],"back substitution")
        return tuple(y)

@dataclass(frozen=True, slots=True)
class IterativeResult:
    solution: tuple
    residual_inf: float
    iterations: int
    converged: bool
    reason: str

def stationary_solve(matrix,b,*,method="gauss_seidel",x0=None,rtol=1e-8,atol=1e-12,max_iter=1000):
    """Jacobi or Gauss-Seidel on a tridiagonal system; O(n) per sweep.

    Convergence is not guaranteed for arbitrary matrices. Stop using the
    true infinity residual <= atol + rtol*||b||inf; no iterate-only test.
    No history retained. Return nonconvergence explicitly.
    """
    if not isinstance(matrix,Tridiagonal):
        raise TypeError("Expected a Tridiagonal operator")
    if method not in ("jacobi","gauss_seidel"):
        raise ValueError("Unknown stationary method")
    max_iter=count(max_iter,"max_iter")
    rtol,atol=finite(rtol,"rtol"),finite(atol,"atol")
    if rtol<0 or atol<0 or not (rtol or atol):
        raise ValueError("Nonnegative tolerances, at least one positive")
    n=len(matrix); b=matrix.vector(b)
    if any(d==0 for d in matrix.diagonal):
        raise ValueError("Stationary methods require a nonzero diagonal")
    x=list(matrix.vector(x0)) if x0 is not None else [0.0]*n
    tol=finite(atol+rtol*max(map(abs,b)),"residual tolerance")
    residual=matrix.residual_inf(x,b)
    if residual<=tol:
        return IterativeResult(tuple(x),residual,0,True,"initial residual")
    for iteration in range(1,max_iter+1):
        old=x if method=="jacobi" else None
        target=[0.0]*n if old is not None else x
        changed=False
        for i in range(n):
            left=matrix.lower[i-1]*x[i-1] if i else 0.0
            right=matrix.upper[i]*x[i+1] if i+1<n else 0.0
            value=finite(fsum((b[i],-left,-right))/matrix.diagonal[i],"iterate")
            changed |= value!=x[i]
            target[i]=value
        x=target
        residual=matrix.residual_inf(x,b)
        if residual<=tol:
            return IterativeResult(tuple(x),residual,iteration,True,"residual tolerance")
        if not changed:
            return IterativeResult(tuple(x),residual,iteration,False,"floating-point stagnation")
    return IterativeResult(tuple(x),residual,max_iter,False,"iteration limit")
