"""Composite quadrature on a finite interval, for smooth scalar integrands."""
from math import fsum
from itertools import chain
from ._validation import finite, count, evaluate

def _grid(a,b,n):
    a,b = finite(a,"a"),finite(b,"b")
    h = finite((b-a)/n,"grid spacing")
    if a != b and (h == 0 or a+h == a or b-h == b):
        raise ValueError("Grid spacing is not representable")
    return a,b,h

def trapezoidal(f,a,b,*,n=100):
    """Composite trapezoidal rule, O(h^2) for sufficiently smooth f."""
    n=count(n,"n")
    a,b,h=_grid(a,b,n)
    if a == b: return 0.0
    total=fsum(chain((evaluate(f,a)/2,evaluate(f,b)/2), (evaluate(f,a+i*h) for i in range(1,n))))
    return finite(h*total,"integral")

def midpoint(f,a,b,*,n=100):
    """Composite midpoint rule, O(h^2) for sufficiently smooth f."""
    n=count(n,"n")
    a,b,h=_grid(a,b,n)
    if a == b: return 0.0
    return finite(h*fsum(evaluate(f,a+(i+.5)*h) for i in range(n)),"integral")

def simpson(f,a,b,*,n=100):
    """Composite Simpson 1/3 rule; n even, O(h^4) for smooth f."""
    n=count(n,"n",2)
    if n%2: raise ValueError("Simpson 1/3 requires an even n")
    a,b,h=_grid(a,b,n)
    if a == b: return 0.0
    total=fsum(chain((evaluate(f,a),evaluate(f,b)), ((4 if i%2 else 2)*evaluate(f,a+i*h) for i in range(1,n))))
    return finite(h*total/3,"integral")

def simpson38(f,a,b,*,n=99):
    """Composite Simpson 3/8 rule; n divisible by 3."""
    n=count(n,"n",3)
    if n%3: raise ValueError("Simpson 3/8 requires n divisible by 3")
    a,b,h=_grid(a,b,n)
    if a == b: return 0.0
    total=fsum(chain((evaluate(f,a),evaluate(f,b)), ((3 if i%3 else 2)*evaluate(f,a+i*h) for i in range(1,n))))
    return finite(3*h*total/8,"integral")
