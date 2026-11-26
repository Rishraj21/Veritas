"""Scalar real root finding with explicit convergence and failure metadata."""
from dataclasses import dataclass
from ._validation import finite, positive, count, evaluate

@dataclass(frozen=True)
class RootResult:
    root: float
    residual: float
    iterations: int
    converged: bool
    reason: str

def _settings(xtol, ftol, max_iter):
    return positive(xtol, "xtol"), positive(ftol, "ftol"), count(max_iter, "max_iter")

def _result(x, fx, i, ok, reason):
    return RootResult(x, abs(fx), i, ok, reason)

def bisection(f, a, b, *, xtol=1e-10, ftol=1e-10, max_iter=200):
    """Bracketed root for a continuous function with opposite endpoint signs.

    A non-exact root is accepted only when both the bracket half-width and
    absolute residual meet tolerances. All x/f tolerances use caller units.
    """
    xtol, ftol, max_iter = _settings(xtol, ftol, max_iter)
    a, b = finite(a, "a"), finite(b, "b")
    if a >= b:
        raise ValueError("a must be less than b")
    fa, fb = evaluate(f,a), evaluate(f,b)
    if fa == 0: return _result(a,fa,0,True,"exact")
    if fb == 0: return _result(b,fb,0,True,"exact")
    if (fa > 0) == (fb > 0):
        raise ValueError("Endpoint values must have opposite signs")
    for i in range(1,max_iter+1):
        x = a/2 + b/2
        fx = evaluate(f,x)
        if fx == 0:
            return _result(x,fx,i,True,"exact")
        if b/2-a/2 <= xtol and abs(fx) <= ftol:
            return _result(x,fx,i,True,"tolerances")
        if x == a or x == b:
            return _result(x,fx,i,False,"floating-point stagnation")
        if (fx > 0) == (fa > 0):
            a, fa = x, fx
        else:
            b, fb = x, fx
    return _result(x,fx,max_iter,False,"iteration limit")

def newton(f, df, x0, *, xtol=1e-10, ftol=1e-10, max_iter=100):
    """Newton-Raphson with caller-supplied derivative; local convergence only."""
    xtol, ftol, max_iter = _settings(xtol,ftol,max_iter)
    x = finite(x0,"x0")
    fx = evaluate(f,x)
    if fx == 0: return _result(x,fx,0,True,"exact")
    for i in range(1,max_iter+1):
        slope = evaluate(df,x)
        if slope == 0:
            return _result(x,fx,i-1,False,"zero derivative")
        y = finite(x-fx/slope,"iterate")
        fy = evaluate(f,y)
        if fy == 0 or (abs(y-x) <= xtol and abs(fy) <= ftol):
            return _result(y,fy,i,True,"exact" if fy == 0 else "tolerances")
        if y == x:
            return _result(y,fy,i,False,"floating-point stagnation")
        x,fx = y,fy
    return _result(x,fx,max_iter,False,"iteration limit")

def secant(f, x0, x1, *, xtol=1e-10, ftol=1e-10, max_iter=100):
    """Derivative-free secant method; no global convergence guarantee."""
    xtol, ftol, max_iter = _settings(xtol,ftol,max_iter)
    a,b = finite(x0,"x0"),finite(x1,"x1")
    if a == b: raise ValueError("Initial points must differ")
    fa,fb = evaluate(f,a),evaluate(f,b)
    if fa == 0: return _result(a,fa,0,True,"exact")
    if fb == 0: return _result(b,fb,0,True,"exact")
    for i in range(1,max_iter+1):
        d = finite(fb-fa,"residual difference")
        if d == 0: return _result(b,fb,i-1,False,"equal function values")
        c = finite(b-(fb/d)*(b-a),"iterate")
        fc = evaluate(f,c)
        if fc == 0 or (abs(c-b) <= xtol and abs(fc) <= ftol):
            return _result(c,fc,i,True,"exact" if fc == 0 else "tolerances")
        if c == b: return _result(c,fc,i,False,"floating-point stagnation")
        a,fa,b,fb = b,fb,c,fc
    return _result(b,fb,max_iter,False,"iteration limit")
