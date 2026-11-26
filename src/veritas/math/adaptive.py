"""Adaptive Bogacki-Shampine 3(2) integration for nonstiff IVPs."""
from dataclasses import dataclass
from math import fsum
from ._validation import finite, positive, count


@dataclass(frozen=True, slots=True)
class AdaptiveResult:
    t: tuple
    y: tuple
    accepted: int
    rejected: int
    evaluations: int
    converged: bool
    reason: str


def rk23(f, t_span, y0, *, rtol=1e-6, atol=1e-9, first_step=None,
         max_step=None, max_attempts=100000, store_every=1):
    """Adaptive explicit RK3(2), with componentwise local error control.

    Scalar or vector state; positive scalar tolerances in consistent units.
    The last derivative is reused on acceptance (FSAL). Rejected trials
    reuse the initial derivative. No stiffness, events or dense output.
    Local tolerance is not a guaranteed bound on global solution error.
    """
    a,b=(finite(t,"time") for t in t_span)
    rtol,atol=positive(rtol,"rtol"),positive(atol,"atol")
    max_attempts=count(max_attempts,"max_attempts")
    store_every=count(store_every,"store_every")
    scalar=isinstance(y0,(int,float))
    def state(v):
        out=(finite(v,"state"),) if scalar else tuple(finite(x,"state") for x in v)
        if not out: raise ValueError("Empty state")
        return out
    y=state(y0); dim=len(y)
    def public(v): return v[0] if scalar else v
    calls=0
    def rhs(t,v):
        nonlocal calls
        calls+=1
        out=state(f(t,public(v)))
        if len(out)!=dim: raise ValueError("RHS dimension mismatch")
        return out
    span=finite(abs(b-a),"time span")
    cap=positive(max_step,"max_step") if max_step is not None else span
    start=positive(first_step,"first_step") if first_step is not None else span/100
    ts=[a]; ys=[public(y)]; t=a; accepted=rejected=0
    def finish(ok,reason):
        if ts[-1]!=t: ts.append(t); ys.append(public(y))
        return AdaptiveResult(tuple(ts),tuple(ys),accepted,rejected,calls,ok,reason)
    if a==b: return finish(True,"endpoint reached")
    direction=1 if b>a else -1
    step=min(start,cap,span)
    k1=rhs(t,y)
    for _ in range(max_attempts):
        remaining=abs(b-t)
        nxt=b if step>=remaining else t+direction*step
        h=nxt-t
        if h==0 or direction*h<=0:
            return finish(False,"step size stagnation")
        k2=rhs(t+h/2,tuple(finite(v+h*(p/2),"stage") for v,p in zip(y,k1)))
        k3=rhs(t+3*h/4,tuple(finite(v+h*(3*q/4),"stage") for v,q in zip(y,k2)))
        trial=tuple(finite(v+h*fsum((2*p/9,q/3,4*r/9)),"trial")
                    for v,p,q,r in zip(y,k1,k2,k3))
        k4=rhs(nxt,trial)
        # Direct embedded difference avoids subtracting two nearly equal states.
        error=0.0
        for v,w,p,q,r,s in zip(y,trial,k1,k2,k3,k4):
            scale=finite(atol+rtol*max(abs(v),abs(w)),"error scale")
            diff=finite(h*fsum((-5*p/72,q/12,r/9,-s/8)),"local error")
            error=max(error,abs(diff)/scale)
        if error<=1:
            t,y,k1=nxt,trial,k4
            accepted+=1
            if accepted%store_every==0 or t==b:
                ts.append(t); ys.append(public(y))
            if t==b: return finish(True,"endpoint reached")
        else:
            rejected+=1
        factor=5.0 if error==0 else max(.2,min(5.0,.9*error**(-1/3)))
        step=min(cap,abs(h)*factor)
    return finish(False,"attempt limit")
