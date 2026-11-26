# Browser-first hybrid numerical architecture

Approved product direction: browser local by default; optional Python backend for advanced numerical tasks. Avoid downloading a full scientific Python runtime to the browser. ES modules load directly; no JS package dependencies or bundler. Heavy work runs in a dedicated module Web Worker, cancelled by termination. Return typed arrays with transferable buffers instead of copying output data. Browser input transfers must explicitly specify a transfer list if the caller wants to avoid copying; the demo only sends scalar settings or a File object.

| Method | Browser | Optional Python |
|---|---|---|
| Matrix-free SPD CG | Float64Array, true residual | Packed Python CG / SciPy |
| CSR sparse | Float64 values, Uint32 indices, no dense assembly | SciPy CSR |
| Nonsymmetric Krylov | BiCGSTAB; bounded restarted GMRES on failure | SciPy adapter |
| Geometric multigrid | 2^k-1 square uniform Poisson, weighted Jacobi, full-weighting restriction, bilinear prolongation | Research prototype |
| Compiled stencil | WASM 386-byte module, explicit fixed-size linear memory; JS fallback available by selecting JS | Numba |
| Streaming | Local File/Blob chunks, scaled L2 norm | Existing iterable norms |
| Tensor contraction | Three one-dimensional contractions, no Kronecker product | Research prototype |
| Restarted Lanczos | Not yet available locally | SciPy ARPACK residual/orthogonality checked adapter |
| Mixed precision / AMR / AMG / JFNK / ROM | Deferred or experimental | Prior research only |

The worker supports Poisson, CSR, tensor and file requests. UI currently exposes Poisson and file norms. There is no browser-to-Python endpoint, remote execution service or hosted deployment. Python partial_eigenpairs accepts a sparse matrix or LinearOperator, with caller-declared symmetry, basis budget and independent relative residual and orthogonality checks. A partial result is returned on ARPACK nonconvergence; no physical accuracy or spectrum completeness certification.

## Numerical resource policy

Default per-job typed-array payload budget 64 MiB; the worker accounts for owned RHS and operator arrays where applicable. Core functions count their work arrays separately from caller-owned inputs. GMRES budget includes basis and small Hessenberg workspace and retained earlier solution. JS heap, garbage collection, serialization overhead, underlying Blob storage, browser process RSS and native allocations are not hard capped. WASM explicitly allocates two float64 views with 64 KiB page rounding; its apply adapter copies input/output, so acceleration is not guaranteed to save end-to-end time or memory. The streaming tool reads at most one chunk per iteration, not entire file; no disk-backed transient trajectory or full out-of-core solver yet.

## Verification

Local Node 22.16.0: six test groups passed. Tests cover comparison of CG and multigrid, nonsymmetric CSR, breakdown and budget-limited fallback, WASM equality for rectangular grids, factorized tensor contraction vs direct product and file chunk processing. Local Python: two spectral tests passed against a reconstructed helper subset, not the full package. Previous full CI passed. Exact source/test blob hashes match local files. Full browser UI smoke could not be completed in the local sandbox because navigation is blocked. Hosted Chromium smoke subsequently passed at commit 8f9689a in [CI run 45908621394](https://github.com/Rishraj21/Veritas/actions/runs/45908621394), including real HTTP-served module loading, the three Poisson solver choices, local file norm calculation and cancellation. All seven jobs passed, including four base Python versions and two accelerated configurations. This verifies a headless Chromium integration test, not public hosting, cross-browser compatibility or production readiness.

Representative single-run Node measurements (unit discrete load, relative residual <= 1e-9, no warm-up protocol, work arrays only): for n=255, CG 510 iterations, 394.06 ms, 2,080,800 bytes; multigrid 12 cycles, 70.07 ms, 2,072,832 bytes. Relative residuals 9.60e-10 and 3.03e-10 respectively. Not browser measurements or universal speedups. No claim that multigrid works for variable coefficients, anisotropy or irregular grids. Core solvers use float64 and require known operator properties; extreme scales and breakdown remain limitations.

## Run

python -m http.server 8000 --directory web

Open localhost:8000. Run node --test tests/browser.test.mjs for kernel tests. The static site may be hosted on any HTTPS static host; no backend required for current browser features. No external packages loaded by the browser.
