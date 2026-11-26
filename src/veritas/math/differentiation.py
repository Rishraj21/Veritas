"""Scalar finite-difference derivatives with explicit step size."""
from ._validation import finite, positive, evaluate

def derivative(f,x,*,h,method="central"):
    """First derivative: forward/backward O(h), central O(h^2) in truncation."""
    x,h=finite(x,"x"),positive(h,"h")
    if method not in ("forward","backward","central"):
        raise ValueError("Unknown difference method")
    if method != "backward" and finite(x+h,"x+h")==x:
        raise ValueError("h too small to resolve x+h")
    if method != "forward" and finite(x-h,"x-h")==x:
        raise ValueError("h too small to resolve x-h")
    if method=="forward":
        xp=x+h
        value=(evaluate(f,xp)-evaluate(f,x))/(xp-x)
    elif method=="backward":
        xm=x-h
        value=(evaluate(f,x)-evaluate(f,xm))/(x-xm)
    else:
        xp,xm=x+h,x-h
        value=(evaluate(f,xp)-evaluate(f,xm))/(xp-xm)
    return finite(value,"derivative")

def second_derivative(f,x,*,h):
    """Three-point central second derivative; smooth f, O(h^2) truncation."""
    x,h=finite(x,"x"),positive(h,"h")
    xp,xm=finite(x+h,"x+h"),finite(x-h,"x-h")
    hp,hm=xp-x,x-xm
    if hp <= 0 or hm <= 0:
        raise ValueError("h too small to resolve neighbours")
    # Nonuniform three-point formula accounts for rounded node positions.
    right=(evaluate(f,xp)-evaluate(f,x))/hp
    left=(evaluate(f,x)-evaluate(f,xm))/hm
    return finite(2*((right-left)/(hp+hm)),"second derivative")
