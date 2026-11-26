"""Shared scalar validation for numerical algorithms."""
from math import isfinite

def finite(value, name="value"):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite real number")
    try:
        x = float(value)
    except OverflowError as exc:
        raise ValueError(f"{name} must be a finite real number") from exc
    if not isfinite(x):
        raise ValueError(f"{name} must be a finite real number")
    return x

def positive(value, name):
    x = finite(value, name)
    if x <= 0:
        raise ValueError(f"{name} must be positive")
    return x

def count(value, name, minimum=1):
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value

def evaluate(f, x):
    return finite(f(x), "function value")
