"""Explicit engineering unit conversion; no guessed units or expression evaluation.

Numeric inputs use the benchmark's SI unit. Tagged values carry an explicit
unit selected from a dimension-specific whitelist. Temperature differences
use a separate conversion path, so offsets are never applied to tolerances.
"""
from collections.abc import Mapping
from math import pi, isfinite

# Maps a reference unit to {accepted unit: (scale, offset)}.
# Each reference unit is also accepted unchanged.
_UNITS = {
    "m": {"mm": (1e-3, 0), "cm": (1e-2, 0), "km": (1e3, 0), "in": (.0254, 0)},
    "m^2": {"mm^2": (1e-6, 0), "cm^2": (1e-4, 0), "in^2": (.0254**2, 0)},
    "m^4": {"mm^4": (1e-12, 0), "cm^4": (1e-8, 0), "in^4": (.0254**4, 0)},
    "m/s": {"mm/s": (1e-3, 0), "cm/s": (1e-2, 0), "km/h": (1/3.6, 0)},
    "m^3/s": {"L/s": (1e-3, 0), "L/min": (1e-3/60, 0), "m^3/h": (1/3600, 0)},
    "Pa": {"kPa": (1e3, 0), "MPa": (1e6, 0), "GPa": (1e9, 0), "bar": (1e5, 0)},
    "Pa/m": {"kPa/m": (1e3, 0), "MPa/m": (1e6, 0), "Pa/mm": (1e3, 0)},
    "Pa s": {"mPa s": (1e-3, 0), "cP": (1e-3, 0)},
    "N": {"kN": (1e3, 0), "mN": (1e-3, 0)},
    "N m": {"N mm": (1e-3, 0), "kN m": (1e3, 0)},
    "rad": {"deg": (pi/180, 0)},
    "K": {"degC": (1, 273.15), "degF": (5/9, 255.3722222222222)},
    "s": {"ms": (1e-3, 0), "min": (60, 0), "h": (3600, 0)},
    "kg": {"g": (1e-3, 0), "mg": (1e-6, 0)},
    "W": {"kW": (1e3, 0), "mW": (1e-3, 0)},
    "Hz": {"kHz": (1e3, 0), "rpm": (1/60, 0)},
    "N/m": {"N/mm": (1e3, 0), "kN/m": (1e3, 0)},
    "J/(kg K)": {"kJ/(kg K)": (1e3, 0)},
    "W/(m K)": {},
    "W/(m^2 K)": {},
}


def _number(value, label):
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise ValueError(f"{label} must be a finite number")
    try:
        result = float(value)
    except OverflowError as exc:
        raise ValueError(f"{label} must be a finite number") from exc
    if not isfinite(result):
        raise ValueError(f"{label} must be a finite number")
    return result


def to_si(value, target, *, difference=False, label="value"):
    """Convert a number or {'value': number, 'unit': str} to target SI units.

    For temperature differences (e.g. absolute error tolerances), accepted
    non-SI units are delta_degC and delta_degF, never absolute degC/degF.
    """
    if not isinstance(value, Mapping):
        return _number(value, label)
    if set(value) != {"value", "unit"} or not isinstance(value["unit"], str):
        raise ValueError(f"{label}: expected exactly value and unit")
    number = _number(value["value"], label)
    unit = value["unit"]
    if unit == target:
        return number
    if difference and target == "K":
        options = {"delta_degC": (1, 0), "delta_degF": (5/9, 0)}
    else:
        options = _UNITS.get(target, {})
    if unit not in options:
        raise ValueError(f"{label}: unit {unit!r} is unsupported or incompatible with {target!r}")
    scale, offset = options[unit]
    return _number(number*scale + offset, label)
