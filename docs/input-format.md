# Input format

Veritas verifies scalar outputs, not entire solver result fields. Inputs are either a JSON object, a JSON array of cases, or a CSV table. Each case has a benchmark ID, parameters and observed quantity; optional id, rtol and atol fields provide identification and tolerances. Unknown case fields are rejected.

## Units

Plain numbers mean SI as defined by the benchmark catalogue. Tagged values have exactly two keys, value (finite number) and unit (case-sensitive string). For instance, 200 GPa may be entered as {"value":200,"unit":"GPa"}. Unit conversion uses an explicit dimension-specific list; arbitrary compound expressions and unknown units are rejected.

Supported alternatives include mm, cm, in, km; mm^2, cm^2, in^2; mm^4, cm^4, in^4; kPa, MPa, GPa, bar; kPa/m, MPa/m, Pa/mm; cP, mPa s; kN, mN, N mm, kN m; L/s, L/min, m^3/h; mm/s, cm/s, km/h; deg, degC, degF; ms, min, h; g, mg; kW, mW; kHz, rpm; N/mm, kN/m; kJ/(kg K). See src/veritas/units.py for exact compatible groups.

A tagged absolute tolerance for a temperature result uses K, delta_degC or delta_degF. Absolute degC and degF cannot be used for error tolerances. Relative tolerance is always dimensionless and based on the SI reference (including absolute temperature in kelvin). All reports are in benchmark SI units.

## CSV

The header must include benchmark and observed. Additional permitted columns are id, observed_unit, rtol, atol, atol_unit, param.NAME and param.NAME.unit. Parameter names must exist in the catalogue and a unit column requires its matching value column. For a mixed benchmark table, leave irrelevant columns blank. Required parameters and observed values must be present for each row. Values are numeric strings, units are exact strings, and omitted units imply SI. Quoted CSV fields are supported. Duplicate headers, malformed rows, unknown parameters and nonfinite values are rejected before a passing report can be produced.

Run veritas describe BENCHMARK to see the required parameter names and output unit. The beam_units examples are synthetic; they demonstrate format and conversion, not solver accuracy.
