# Numerical development standard

Prefer correctness and numerical stability before speed or memory savings. For every algorithm, compare alternatives by physical/mathematical assumptions, convergence, conditioning, arithmetic precision, runtime and auxiliary memory. Record complexity including output storage separately. Benchmark representative and adversarial cases with reproducible inputs; do not claim measured speedups from asymptotic analysis alone.

Use streaming, iterator interfaces, reusable factorizations and sparse or banded structure when appropriate. Do not duplicate equations across domain modules. Preserve API compatibility unless a documented change is necessary. Prefer mature NumPy/SciPy backends for large production systems; do not force their installation for small scalar operations. Keep educational implementations transparent.

Validate independent analytical cases, boundary/invalid inputs, refinement order, numerical residuals, and where feasible independent reference implementations. A lower-memory result must agree with the original method within justified tolerances. Include reproducible resource checks in CI when stable; avoid fragile runtime thresholds.

Review existing modules before expanding scope. Open issues: interpolation repeatedly copies/validates node arrays; consider reusable interpolators for repeated queries. Root-finding tolerance scaling, adaptive integration and extreme-value behavior deserve review. Dense LU remains O(n^2) factor storage, which is not appropriate for large sparse engineering meshes. No current claim of production-scale performance.
