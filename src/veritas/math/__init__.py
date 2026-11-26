"""Educational numerical methods for small scalar engineering problems."""
from .roots import RootResult, bisection, newton, secant
from .integration import trapezoidal, midpoint, simpson, simpson38
from .differentiation import derivative, second_derivative
from .interpolation import linear_interpolate, newton_interpolate

__all__ = ["RootResult", "bisection", "newton", "secant", "trapezoidal",
           "midpoint", "simpson", "simpson38", "derivative", "second_derivative",
           "linear_interpolate", "newton_interpolate"]
