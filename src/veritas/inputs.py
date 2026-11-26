"""Strict, dependency-free CSV case ingestion."""
import csv
from pathlib import Path
import re
from .benchmarks import BENCHMARKS

_BASE = {"id", "benchmark", "observed", "observed_unit", "rtol", "atol", "atol_unit"}
_PARAM = re.compile(r"param\.([A-Za-z_][A-Za-z0-9_]*)(\.unit)?\Z")


def _quantity(row, key, unit_key):
    raw, unit = row.get(key, ""), row.get(unit_key, "")
    if not raw:
        raise ValueError(f"Missing {key}")
    value = float(raw)
    return {"value": value, "unit": unit} if unit else value


def read_csv(path):
    """Read one benchmark case per row. Unlabelled numeric values are SI.

    Parameters use param.NAME and optional param.NAME.unit columns.
    Nonempty parameters not used by a row's benchmark are rejected.
    """
    cases = []
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream, strict=True)
        try:
            headers = next(reader)
        except StopIteration as exc:
            raise ValueError("CSV has no header") from exc
        headers = [h.strip() for h in headers]
        if len(set(headers)) != len(headers):
            raise ValueError("Duplicate CSV header")
        if not {"benchmark", "observed"}.issubset(headers):
            raise ValueError("CSV requires benchmark and observed headers")
        all_params = {k for spec in BENCHMARKS.values() for k in spec.parameters}
        for header in headers:
            if header in _BASE:
                continue
            match = _PARAM.fullmatch(header)
            if not match or match[1] not in all_params:
                raise ValueError(f"Unknown CSV column: {header}")
            if match[2] and "param."+match[1] not in headers:
                raise ValueError(f"Unit column without value column: {header}")
        if "atol_unit" in headers and "atol" not in headers:
            raise ValueError("atol_unit requires atol column")
        for cells in reader:
            line = reader.line_num
            if not cells or not any(x.strip() for x in cells):
                continue
            if len(cells) != len(headers):
                raise ValueError(f"CSV line {line}: incorrect number of fields")
            row = dict(zip(headers, (x.strip() for x in cells)))
            try:
                name = row["benchmark"]
                if name not in BENCHMARKS:
                    raise ValueError(f"Unknown benchmark: {name}")
                required = BENCHMARKS[name].parameters
                for key, val in row.items():
                    match = _PARAM.fullmatch(key)
                    if match and val and match[1] not in required:
                        raise ValueError(f"Unexpected parameter for {name}: {key}")
                params = {k: _quantity(row, "param."+k, "param."+k+".unit") for k in required}
                case = {"benchmark": name, "parameters": params,
                        "observed": _quantity(row, "observed", "observed_unit")}
                if row.get("id"):
                    case["id"] = row["id"]
                if row.get("rtol"):
                    case["rtol"] = float(row["rtol"])
                if row.get("atol") or row.get("atol_unit"):
                    case["atol"] = _quantity(row, "atol", "atol_unit")
                cases.append(case)
            except ValueError as exc:
                raise ValueError(f"CSV line {line}: {exc}") from exc
    if not cases:
        raise ValueError("CSV has no cases")
    return cases
