"""Reusable interpolation on finite, strictly increasing nodes."""
from bisect import bisect_right
from dataclasses import dataclass
from ._validation import finite

def _nodes(xs,ys):
    xs=tuple(finite(t,"node") for t in xs)
    ys=tuple(finite(t,"value") for t in ys)
    if len(xs)!=len(ys) or len(xs)<2:
        raise ValueError("At least two paired nodes are required")
    if any(a>=b for a,b in zip(xs,xs[1:])):
        raise ValueError("Nodes must be strictly increasing")
    return xs,ys

def _interval(xs,x):
    x=finite(x,"x")
    if not xs[0]<=x<=xs[-1]:
        raise ValueError("Extrapolation is not supported")
    return x,min(bisect_right(xs,x)-1,len(xs)-2)

@dataclass(frozen=True, slots=True, init=False)
class LinearInterpolator:
    """Validate once in O(n); each query needs O(log n) work and O(1) space."""
    xs: tuple
    ys: tuple

    def __init__(self,xs,ys):
        x,y=_nodes(xs,ys)
        object.__setattr__(self,"xs",x)
        object.__setattr__(self,"ys",y)

    def __call__(self,x):
        x,i=_interval(self.xs,x)
        a,b=self.xs[i],self.xs[i+1]
        if x==a: return self.ys[i]
        if x==b: return self.ys[i+1]
        # Halve first when the full node span would overflow.
        span=b-a
        t=(x-a)/span if span!=float("inf") else (x/2-a/2)/(b/2-a/2)
        return finite((1-t)*self.ys[i]+t*self.ys[i+1],"interpolated value")

@dataclass(frozen=True, slots=True, init=False)
class NewtonInterpolator:
    """O(n^2) setup, O(n) storage and O(n) query for small well-scaled data."""
    xs: tuple
    ys: tuple
    coefficients: tuple

    def __init__(self,xs,ys):
        xs,ys=_nodes(xs,ys)
        c=list(ys)
        n=len(xs)
        for j in range(1,n):
            for i in range(n-1,j-1,-1):
                span=finite(xs[i]-xs[i-j],"node span")
                c[i]=finite((c[i]-c[i-1])/span,"divided difference")
        object.__setattr__(self,"xs",xs)
        object.__setattr__(self,"ys",ys)
        object.__setattr__(self,"coefficients",tuple(c))

    def __call__(self,x):
        x,i=_interval(self.xs,x)
        if x==self.xs[i]: return self.ys[i]
        if x==self.xs[i+1]: return self.ys[i+1]
        c=self.coefficients
        result=c[-1]
        for i in range(len(c)-2,-1,-1):
            result=finite(c[i]+(x-self.xs[i])*result,"interpolated value")
        return result

def linear_interpolate(xs,ys,x):
    """One-shot piecewise linear interpolation."""
    return LinearInterpolator(xs,ys)(x)

def newton_interpolate(xs,ys,x):
    """One-shot Newton polynomial interpolation. Avoid high-degree data fits."""
    return NewtonInterpolator(xs,ys)(x)
