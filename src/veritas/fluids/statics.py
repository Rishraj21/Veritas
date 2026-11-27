"""Constant-density statics and idealized compressible hydrostatics (SI)."""
from math import exp, log1p, sin, pi
from dataclasses import dataclass
from collections.abc import Iterable


def f(x):
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        raise ValueError('Expected finite real number')
    from math import isfinite
    if not isfinite(x):
        raise ValueError('Expected finite real number')
    return float(x)


def p(x):
    x = f(x)
    if x <= 0: raise ValueError('Expected positive number')
    return x


def nn(x):
    x = f(x)
    if x < 0: raise ValueError('Expected nonnegative number')
    return x


@dataclass(frozen=True, slots=True)
class PressurePath:
    delta: float
    pressure: float


def pressure_path(segments: Iterable, surface_pressure=0., g=9.80665):
    """Stream (density, upward elevation change) pairs; no interface jumps."""
    g = p(g); initial = f(surface_pressure); total = correction = 0.
    for rho, dz in segments:
        term = f(-p(rho)*g*f(dz))
        updated = f(total+term)
        correction = f(correction + ((total-updated)+term if abs(total)>=abs(term) else (term-updated)+total))
        total = updated
    delta = f(total+correction)
    return PressurePath(delta, f(initial+delta))


def gas_pressure(p0, dz, gas_constant, temperature, lapse=0., g=9.80665):
    """Ideal gas with T(z)=temperature+lapse*dz; positive absolute pressure."""
    p0, dz, R, T, L, g = p(p0), f(dz), p(gas_constant), p(temperature), f(lapse), p(g)
    x = f(L*dz/T)
    if x <= -1: raise ValueError('Temperature must stay positive')
    factor = log1p(x)/x if x else 1.
    try: return p(p0*exp(-g*dz/R/T*factor))
    except OverflowError as exc: raise ValueError('Pressure overflow') from exc


def liquid_pressure_change(rho, depth, bulk_modulus, g=9.80665):
    """Idealized constant bulk modulus, signed downward depth."""
    K = p(bulk_modulus); x = f(p(rho)*p(g)*f(depth)/K)
    if x >= 1: raise ValueError('Constant-K model singularity')
    return f(-K*log1p(-x))


def plane_force(area, centroid_pressure):
    """Signed net normal force on a fully wetted plane, linear pressure."""
    return f(p(area)*f(centroid_pressure))


def plane_moment(rho, inertia, angle, g=9.80665):
    """Signed first moment of pressure about centroid, downhill coordinate."""
    angle = f(angle)
    if not 0 <= angle <= pi/2: raise ValueError('Angle must be in [0, pi/2]')
    return f(p(rho)*p(g)*nn(inertia)*sin(angle))


def pressure_offset(force, moment):
    """Downhill offset from centroid; undefined when resultant is zero."""
    force = f(force)
    if not force: raise ValueError('Zero resultant has no unique pressure center')
    return f(f(moment)/force)


def floating_fraction(body_density, fluid_density):
    """Uniform body at a free surface, negligible gas buoyancy."""
    ratio = p(body_density)/p(fluid_density)
    if ratio > 1: raise ValueError('Body cannot float in this fluid')
    return f(ratio)


def metacentric_height(kb, kg, inertia, volume):
    """Initial small-angle stability only, common vertical datum and heel axis."""
    return f(f(kb)-f(kg)+nn(inertia)/p(volume))


def translating_pressure_change(rho, dx, dz, ax, az, g=9.80665):
    """Constant acceleration, z upward, gravity downward."""
    return f(-p(rho)*(f(ax)*f(dx)+(p(g)+f(az))*f(dz)))


def rotation_level_change(omega, r1, r2, g=9.80665):
    """Rigid-body rotation, vertical axis; free surface level difference."""
    w, a, b = f(omega), nn(r1), nn(r2)
    return f(w*w*(b-a)*(b+a)/(2*p(g)))
