"""Explicit scalar comparison with absolute and relative tolerances."""
from dataclasses import asdict, dataclass
from collections.abc import Mapping
from .benchmarks import BENCHMARKS, finite_number, reference


class CheckError(ValueError):
    """Invalid check input (rather than a failed physical comparison)."""


@dataclass(frozen=True)
class CheckResult:
    benchmark: str
    quantity: str
    unit: str
    expected: float
    observed: float
    absolute_error: float
    relative_error: float | None
    allowed_error: float
    passed: bool
    assumptions: str

    def to_dict(self):
        return asdict(self)


def check(benchmark, parameters, observed, *, rtol=0.01, atol=0.0):
    """Pass iff |observed-reference| <= atol + rtol*|reference|.

    atol uses the benchmark output SI unit. Relative error is undefined at
    a zero reference and is reported as None. A pass is not solver validation.
    """
    try:
        expected = reference(benchmark, parameters)
        observed = finite_number(observed, "observed")
        rtol = finite_number(rtol, "rtol")
        atol = finite_number(atol, "atol")
        if min(rtol, atol) < 0:
            raise ValueError("tolerances must be nonnegative")
        error = finite_number(abs(observed - expected), "absolute error")
        limit = finite_number(atol + rtol * abs(expected), "allowed error")
        relative = None if expected == 0 else finite_number(error/abs(expected), "relative error")
    except (ValueError, TypeError, OverflowError) as exc:
        raise CheckError(str(exc)) from exc
    spec = BENCHMARKS[benchmark]
    return CheckResult(benchmark, spec.quantity, spec.output_unit, expected, observed, error, relative, limit, error <= limit, spec.assumptions)


def check_case(case):
    if not isinstance(case, Mapping):
        raise CheckError("Each case must be an object")
    required = {"benchmark", "parameters", "observed"}
    allowed = required | {"id", "rtol", "atol"}
    if required - case.keys() or case.keys() - allowed:
        raise CheckError(f"Invalid case fields: missing={sorted(required-case.keys())}, unexpected={sorted(case.keys()-allowed)}")
    if not isinstance(case["benchmark"], str):
        raise CheckError("benchmark must be a string")
    if "id" in case and not isinstance(case["id"], str):
        raise CheckError("id must be a string")
    return check(case["benchmark"], case["parameters"], case["observed"], rtol=case.get("rtol", 0.01), atol=case.get("atol", 0.0))
