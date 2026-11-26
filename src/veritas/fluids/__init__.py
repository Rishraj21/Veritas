"""Introductory fluid properties and statics. All arguments are SI."""
from math import cos, pi
from ..math._validation import finite, positive


def _nonnegative(x, name):
    x = finite(x, name)
    if x < 0:
        raise ValueError(f'{name} must be nonnegative')
    return x


def density(mass, volume):
    return finite(positive(mass, 'mass') / positive(volume, 'volume'))


def specific_volume(rho):
    return finite(1 / positive(rho, 'density'))


def specific_weight(rho, g=9.80665):
    return finite(positive(rho, 'density') * positive(g, 'gravity'))


def specific_gravity(rho, reference_density):
    return finite(positive(rho, 'density') / positive(reference_density, 'reference density'))


def kinematic_viscosity(mu, rho):
    return finite(positive(mu, 'dynamic viscosity') / positive(rho, 'density'))


def shear_stress(mu, gradient):
    """Signed Newtonian simple-shear stress, tau=mu du/dy."""
    return finite(positive(mu, 'dynamic viscosity') * finite(gradient, 'velocity gradient'))


def compressibility(bulk_modulus):
    """Reciprocal bulk modulus on the same thermodynamic path."""
    return finite(1 / positive(bulk_modulus, 'bulk modulus'))


def volume_strain(delta_p, bulk_modulus):
    """Linearized signed dV/V; valid only for small pressure-induced strains."""
    return finite(-finite(delta_p, 'pressure change') / positive(bulk_modulus, 'bulk modulus'))


def laplace_pressure(sigma, curvature):
    """Signed jump for one interface, curvature=1/R1+1/R2."""
    return finite(_nonnegative(sigma, 'surface tension') * finite(curvature, 'curvature'))


def capillary_rise(sigma, theta, radius, delta_rho, g=9.80665):
    """Circular tube, static meniscus, angle through liquid in radians."""
    theta = finite(theta, 'contact angle')
    if not 0 <= theta <= pi:
        raise ValueError('Contact angle must be in [0, pi]')
    return finite(2 * (_nonnegative(sigma, 'surface tension') / positive(radius, 'radius')) * cos(theta) / positive(delta_rho, 'density difference') / positive(g, 'gravity'))


def hydrostatic_pressure(rho, depth, surface_pressure=0, g=9.80665):
    """Constant density, depth positive down; same pressure datum as surface."""
    return finite(finite(surface_pressure, 'surface pressure') + specific_weight(rho, g) * _nonnegative(depth, 'depth'))


def pressure_head(pressure, rho, g=9.80665):
    return finite(finite(pressure, 'pressure') / specific_weight(rho, g))


def buoyancy(rho, displaced_volume, g=9.80665):
    """Magnitude of upward force in a uniform fluid."""
    return finite(specific_weight(rho, g) * _nonnegative(displaced_volume, 'displaced volume'))
