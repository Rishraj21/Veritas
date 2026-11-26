"""Educational numerical methods for small engineering problems."""
from .roots import RootResult, bisection, newton, secant
from .integration import trapezoidal, midpoint, simpson, simpson38
from .differentiation import derivative, second_derivative
from .interpolation import linear_interpolate, newton_interpolate

__all__ = ["RootResult", "bisection", "newton", "secant", "trapezoidal",
           "midpoint", "simpson", "simpson38", "derivative", "second_derivative",
           "linear_interpolate", "newton_interpolate"]

from .linalg import LUFactor, LinearResult, lu_factor, solve_linear
from .ode import ODEResult, solve_ivp, stability_factor
from .errors import ErrorNorms, error_norms

__all__ += ["LUFactor", "LinearResult", "lu_factor", "solve_linear",
            "ODEResult", "solve_ivp", "stability_factor", "ErrorNorms", "error_norms"]

from .banded import Tridiagonal, TridiagonalFactor, IterativeResult, stationary_solve
from .interpolation import LinearInterpolator, NewtonInterpolator
__all__ += ["Tridiagonal", "TridiagonalFactor", "IterativeResult", "stationary_solve", "LinearInterpolator", "NewtonInterpolator"]
