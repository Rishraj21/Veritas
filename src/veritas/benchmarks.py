"""Closed-form benchmark functions. All numerical inputs and outputs use SI units."""
from dataclasses import dataclass
from math import exp, pi, sqrt, tanh, isfinite
from typing import Callable, Mapping


@dataclass(frozen=True)
class Parameter:
    unit: str
    description: str
    minimum: float | None = None
    strict: bool = False


@dataclass(frozen=True)
class Benchmark:
    title: str
    parameters: Mapping[str, Parameter]
    output_unit: str
    quantity: str
    assumptions: str
    formula: str
    evaluate: Callable[..., float]


def positive(unit, desc):
    return Parameter(unit, desc, 0, True)


def nonnegative(unit, desc):
    return Parameter(unit, desc, 0)


def signed(unit, desc):
    return Parameter(unit, desc)


BENCHMARKS = {
    "pipe_flow": Benchmark("Hagen–Poiseuille pipe flow", {
        "pressure_drop": signed("Pa", "Inlet minus outlet pressure"),
        "radius": positive("m", "Internal radius"),
        "viscosity": positive("Pa s", "Dynamic viscosity"),
        "length": positive("m", "Pipe length"),
    }, "m^3/s", "Volumetric flow rate", "Steady, fully developed, incompressible Newtonian laminar flow; rigid circular pipe; no slip.",
        "Q = pi * dp * r^4 / (8 * mu * L)", lambda pressure_drop, radius, viscosity, length: pi*pressure_drop*radius**4/(8*viscosity*length)),
    "couette_flow": Benchmark("Plane Couette flow", {
        "wall_speed": signed("m/s", "Moving upper wall velocity"),
        "gap": positive("m", "Plate separation"),
        "y": nonnegative("m", "Distance from stationary wall"),
    }, "m/s", "Streamwise velocity", "Steady, fully developed Newtonian flow; lower wall stationary; zero pressure gradient; no slip.",
        "u = U * y / h", lambda wall_speed, gap, y: wall_speed*y/gap),
    "plane_poiseuille": Benchmark("Plane Poiseuille flow", {
        "pressure_gradient": signed("Pa/m", "Negative streamwise pressure gradient (-dp/dx)"),
        "gap": positive("m", "Full plate separation"),
        "viscosity": positive("Pa s", "Dynamic viscosity"),
        "y": nonnegative("m", "Distance from lower plate"),
    }, "m/s", "Streamwise velocity", "Steady, fully developed Newtonian laminar flow; stationary parallel plates; no slip.",
        "u = G * y * (h-y) / (2 * mu)", lambda pressure_gradient, gap, viscosity, y: pressure_gradient*y*(gap-y)/(2*viscosity)),
    "axial_bar": Benchmark("Uniform axially loaded bar", {
        "force": signed("N", "Axial load; tension positive"),
        "length": positive("m", "Bar length"),
        "area": positive("m^2", "Cross-section area"),
        "youngs_modulus": positive("Pa", "Young's modulus"),
    }, "m", "Axial displacement", "Linear elasticity, small deformation, uniform cross-section and axial stress.",
        "delta = F*L/(A*E)", lambda force, length, area, youngs_modulus: force*length/(area*youngs_modulus)),
    "cantilever_tip": Benchmark("Cantilever end-load deflection", {
        "force": signed("N", "Transverse tip load; positive along measured deflection"),
        "length": positive("m", "Beam span"),
        "youngs_modulus": positive("Pa", "Young's modulus"),
        "second_moment": positive("m^4", "Second moment of area about bending axis"),
    }, "m", "Tip deflection", "Slender prismatic Euler–Bernoulli beam; perfect clamp; small linear deflection; negligible shear deformation.",
        "delta = F*L^3/(3*E*I)", lambda force, length, youngs_modulus, second_moment: force*length**3/(3*youngs_modulus*second_moment)),
    "circular_shaft": Benchmark("Circular shaft torsion", {
        "torque": signed("N m", "Applied torque"),
        "length": positive("m", "Shaft length"),
        "shear_modulus": positive("Pa", "Shear modulus"),
        "radius": positive("m", "Solid shaft radius"),
    }, "rad", "Angle of twist", "Uniform solid circular shaft, Saint-Venant torsion, linear elasticity, small twist.",
        "theta = T*L/(G*J), J = pi*r^4/2", lambda torque, length, shear_modulus, radius: 2*torque*length/(shear_modulus*pi*radius**4)),
    "slab_conduction": Benchmark("Steady plane-wall conduction", {
        "conductivity": positive("W/(m K)", "Constant thermal conductivity"),
        "area": positive("m^2", "Heat transfer area"),
        "thickness": positive("m", "Wall thickness"),
        "hot_temperature": nonnegative("K", "Temperature at first face"),
        "cold_temperature": nonnegative("K", "Temperature at second face"),
    }, "W", "Signed heat transfer rate from first to second face", "One-dimensional steady conduction; no internal heat generation; constant conductivity; prescribed face temperatures.",
        "Q = k*A*(T1-T2)/L", lambda conductivity, area, thickness, hot_temperature, cold_temperature: conductivity*area*(hot_temperature-cold_temperature)/thickness),
    "lumped_cooling": Benchmark("Lumped-capacitance cooling or heating", {
        "initial_temperature": nonnegative("K", "Initial body temperature"),
        "ambient_temperature": nonnegative("K", "Constant surrounding temperature"),
        "h": positive("W/(m^2 K)", "Convection coefficient"),
        "area": positive("m^2", "Exposed surface area"),
        "mass": positive("kg", "Body mass"),
        "specific_heat": positive("J/(kg K)", "Constant specific heat"),
        "time": nonnegative("s", "Elapsed time"),
    }, "K", "Body temperature", "Spatially uniform temperature (typically Bi < 0.1); constant coefficients; negligible radiation and internal generation.",
        "T = Tinf + (T0-Tinf)*exp(-h*A*t/(m*cp))", lambda initial_temperature, ambient_temperature, h, area, mass, specific_heat, time: ambient_temperature+(initial_temperature-ambient_temperature)*exp(-h*area*time/(mass*specific_heat))),
    "spring_mass": Benchmark("Undamped spring-mass natural frequency", {
        "stiffness": positive("N/m", "Linear spring stiffness"),
        "mass": positive("kg", "Lumped mass"),
    }, "Hz", "Natural frequency", "Single degree of freedom; undamped, linear spring; negligible spring mass.",
        "f = sqrt(k/m)/(2*pi)", lambda stiffness, mass: sqrt(stiffness/mass)/(2*pi)),
    "insulated_fin": Benchmark("Straight fin with insulated tip", {
        "conductivity": positive("W/(m K)", "Thermal conductivity"),
        "area": positive("m^2", "Uniform cross-sectional area"),
        "perimeter": positive("m", "Exposed perimeter"),
        "h": positive("W/(m^2 K)", "Convection coefficient"),
        "length": positive("m", "Fin length"),
        "base_temperature": nonnegative("K", "Prescribed base temperature"),
        "ambient_temperature": nonnegative("K", "Ambient temperature"),
    }, "W", "Signed base heat transfer rate", "Steady one-dimensional conduction; constant properties; uniform convection; adiabatic tip.",
        "Q = sqrt(h*P*k*A)*(Tb-Tinf)*tanh(L*sqrt(h*P/(k*A)))", lambda conductivity, area, perimeter, h, length, base_temperature, ambient_temperature: sqrt(h*perimeter*conductivity*area)*(base_temperature-ambient_temperature)*tanh(length*sqrt(h*perimeter/(conductivity*area)))),
}


def finite_number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return float(value)


def reference(name: str, parameters: Mapping[str, float]) -> float:
    if name not in BENCHMARKS:
        raise ValueError(f"Unknown benchmark: {name}")
    if not isinstance(parameters, Mapping):
        raise ValueError("parameters must be an object")
    spec = BENCHMARKS[name]
    missing = spec.parameters.keys() - parameters.keys()
    extra = parameters.keys() - spec.parameters.keys()
    if missing or extra:
        raise ValueError(f"Parameter mismatch: missing={sorted(missing)}, unexpected={sorted(extra)}")
    p = {}
    for key, definition in spec.parameters.items():
        v = finite_number(parameters[key], key)
        if definition.minimum is not None and (v < definition.minimum or (definition.strict and v == definition.minimum)):
            relation = ">" if definition.strict else ">="
            raise ValueError(f"{key} must be {relation} {definition.minimum}")
        p[key] = v
    if name in {"couette_flow", "plane_poiseuille"} and p["y"] > p["gap"]:
        raise ValueError("y must lie within the plate gap")
    try:
        result = spec.evaluate(**p)
    except (ArithmeticError, ValueError) as exc:
        raise ValueError(f"Reference evaluation failed: {exc}") from exc
    return finite_number(result, "reference result")
