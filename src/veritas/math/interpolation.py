"""Interpolation on strictly increasing finite nodes; no implicit extrapolation."""
from bisect import bisect_right
from ._validation import finite

def _data(xs,ys,x):
    xs=[finite(t,"node") for t in xs]
    ys=[finite(t,"value") for t in ys]
    x=finite(x,"x")
    if len(xs)!=len(ys) or len(xs)<2:
        raise ValueError("At least two paired nodes are required")
    if any(a>=b for a,b in zip(xs,xs[1:])):
        raise ValueError("Nodes must be strictly increasing")
    if not xs[0]<=x<=xs[-1]:
        raise ValueError("Extrapolation is not supported")
    return xs,ys,x

def linear_interpolate(xs,ys,x):
    """Piecewise linear interpolation, exact for affine data."""
    xs,ys,x=_data(xs,ys,x)
    i=min(bisect_right(xs,x)-1,len(xs)-2)
    if x==xs[i]: return ys[i]
    if x==xs[i+1]: return ys[i+1]
    t=(x-xs[i])/(xs[i+1]-xs[i])
    return finite((1-t)*ys[i]+t*ys[i+1],"interpolated value")

def newton_interpolate(xs,ys,x):
    """Newton divided differences, intended for small well-scaled node sets.

    High-degree interpolation can be ill-conditioned; no error bound provided.
    """
    xs,c,x=_data(xs,ys,x)
    if x in xs: return c[xs.index(x)]
    n=len(xs)
    for j in range(1,n):
        for i in range(n-1,j-1,-1):
            c[i]=finite((c[i]-c[i-1])/(xs[i]-xs[i-j]),"divided difference")
    result=c[-1]
    for i in range(n-2,-1,-1):
        result=finite(c[i]+(x-xs[i])*result,"interpolated value")
    return result
