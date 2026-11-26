"""Solver-independent analytical verification tools."""
from .benchmarks import BENCHMARKS, Benchmark, reference
from .core import CheckResult, CheckError, check, check_case
from .convergence import estimate_order

__version__ = "0.1.0"
__all__ = ["BENCHMARKS", "Benchmark", "reference", "CheckResult", "CheckError", "check", "check_case", "estimate_order"]
