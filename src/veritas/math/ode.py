"""Fixed-step explicit ODE methods for scalar and small vector IVPs."""
from dataclasses import dataclass
from math import fsum
from ._validation import finite,count

@dataclass(frozen=True)
class ODEResult:
    t: tuple
    y: tuple
    method: str
    evaluations: int

def solve_ivp(f,t_span,y0,*,n=100,method="rk4",store_every=1):
    """Integrate y'=f(t,y) with n fixed steps (Euler, midpoint, Heun, RK4).

    Scalar input yields scalar samples; vector input yields tuple samples.
    Supports reverse time. No adaptivity, events, stiffness or error control.
    store_every retains every kth step plus both endpoints; stepping is unchanged.
    """
    n=count(n,"n")
    store_every=count(store_every,"store_every")
    if method not in ("euler","midpoint","heun","rk4"):
        raise ValueError("Unknown ODE method")
    a,b=(finite(t,"time") for t in t_span)
    scalar=isinstance(y0,(int,float))
    def state(v):
        if scalar:
            return (finite(v,"state"),)
        out=tuple(finite(x,"state component") for x in v)
        if not out:
            raise ValueError("Empty vector state")
        return out
    y=state(y0); dim=len(y)
    def public(v):
        return v[0] if scalar else v
    calls=0
    def rhs(t,v):
        nonlocal calls
        calls+=1
        result=state(f(t,public(v)))
        if len(result)!=dim:
            raise ValueError("RHS dimension does not match initial state")
        return result
    def advance(v,k,h):
        return tuple(finite(x+h*dx,"ODE stage") for x,dx in zip(v,k))
    ts=[a]; ys=[public(y)]
    if a==b:
        return ODEResult(tuple(ts),tuple(ys),method,0)
    span=finite(b-a,"time span")
    t=a
    for i in range(n):
        nxt=b if i==n-1 else finite(a+span*((i+1)/n),"time node")
        h=finite(nxt-t,"time step")
        if h==0 or (h>0)!=(span>0):
            raise ValueError("Time grid is not representable")
        k1=rhs(t,y)
        if method=="euler":
            y=advance(y,k1,h)
        elif method=="midpoint":
            k2=rhs(t+h/2,advance(y,k1,h/2))
            y=advance(y,k2,h)
        elif method=="heun":
            k2=rhs(nxt,advance(y,k1,h))
            y=advance(y,tuple(fsum((u/2,v/2)) for u,v in zip(k1,k2)),h)
        else:
            k2=rhs(t+h/2,advance(y,k1,h/2))
            k3=rhs(t+h/2,advance(y,k2,h/2))
            k4=rhs(nxt,advance(y,k3,h))
            slope=tuple(fsum((u/6,v/3,w/3,z/6)) for u,v,w,z in zip(k1,k2,k3,k4))
            y=advance(y,slope,h)
        t=nxt
        if (i+1)%store_every==0 or i==n-1:
            ts.append(nxt); ys.append(public(y))
    return ODEResult(tuple(ts),tuple(ys),method,calls)

def stability_factor(z,method="rk4"):
    """Amplification factor R(z) on y'=lambda*y, z=h*lambda (real or complex).

    |R| <= 1 is the scalar linear absolute stability condition, not a
    general nonlinear or accuracy guarantee.
    """
    from math import isfinite
    if isinstance(z,bool) or not isinstance(z,(int,float,complex)):
        raise ValueError("z must be finite real or complex")
    z=complex(z)
    if not (isfinite(z.real) and isfinite(z.imag)):
        raise ValueError("z must be finite")
    degrees={"euler":1,"midpoint":2,"heun":2,"rk4":4}
    if method not in degrees:
        raise ValueError("Unknown ODE method")
    r=1+0j; term=1+0j
    for j in range(1,degrees[method]+1):
        term=term*z/j
        r+=term
    if not (isfinite(r.real) and isfinite(r.imag)):
        raise ValueError("Nonfinite stability factor")
    return r
