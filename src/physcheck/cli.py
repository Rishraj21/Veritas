"""Command line interface: exit 0 pass, 1 comparison failure, 2 invalid input."""
import argparse
import json
import sys
from pathlib import Path
from .benchmarks import BENCHMARKS
from .core import CheckError, check_case


def _reject_constant(value):
    raise ValueError(f"Non-finite JSON constant: {value}")


def _unique_object(pairs):
    data = {}
    for k, v in pairs:
        if k in data:
            raise ValueError(f"Duplicate JSON key: {k}")
        data[k] = v
    return data


def main(argv=None):
    parser = argparse.ArgumentParser(prog="physcheck", description="Analytical simulation verification checks")
    subs = parser.add_subparsers(dest="command", required=True)
    subs.add_parser("list", help="List available benchmarks")
    describe = subs.add_parser("describe", help="Show benchmark parameters and assumptions")
    describe.add_argument("benchmark", choices=sorted(BENCHMARKS))
    validate = subs.add_parser("validate", help="Evaluate a JSON case or case array")
    validate.add_argument("file", type=Path)
    validate.add_argument("--json", action="store_true", help="Output machine-readable report")
    args = parser.parse_args(argv)
    if args.command == "list":
        for name, spec in BENCHMARKS.items():
            print(f"{name:20} {spec.title} [{spec.output_unit}]")
        return 0
    if args.command == "describe":
        spec = BENCHMARKS[args.benchmark]
        print(f"{spec.title}\n{spec.formula}\nOutput: {spec.quantity} [{spec.output_unit}]\nAssumptions: {spec.assumptions}\nParameters:")
        for name, p in spec.parameters.items():
            print(f"  {name} [{p.unit}]: {p.description}")
        return 0
    try:
        payload = json.loads(args.file.read_text(encoding="utf-8"), parse_constant=_reject_constant, object_pairs_hook=_unique_object)
        cases = payload if isinstance(payload, list) else [payload]
        if not cases:
            raise CheckError("At least one case is required")
        results = []
        for i, case in enumerate(cases):
            try:
                result = check_case(case).to_dict()
            except CheckError as exc:
                raise CheckError(f"Case {i+1}: {exc}") from exc
            result["id"] = case.get("id", str(i+1))
            results.append(result)
        passed = sum(r["passed"] for r in results)
        if args.json:
            print(json.dumps({"passed": passed, "total": len(results), "results": results}, indent=2, allow_nan=False))
        else:
            for r in results:
                print(f"{'PASS' if r['passed'] else 'FAIL'} {r['id']} ({r['benchmark']}): observed={r['observed']:.8g}, reference={r['expected']:.8g} {r['unit']}, abs_error={r['absolute_error']:.3g}, limit={r['allowed_error']:.3g}")
            print(f"{passed}/{len(results)} checks passed. Review benchmark assumptions before interpreting results.")
        return 0 if passed == len(results) else 1
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        print(f"physcheck: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
