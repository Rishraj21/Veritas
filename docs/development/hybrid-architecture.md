# Approved aggressive hybrid architecture

Keep the base installation dependency-free. Choose a representation from known mathematical structure; never infer SPD merely from matrix shape or a successful solve. Use float64 by default. Explicitly opt in to acceleration and precision changes. Independently check residuals and convergence; verify discretization errors separately. Complexity budgets must distinguish numeric payload, Python traced allocations and RSS.

## Integration status

| Technique | Policy | Status |
|---|---|---|
| Packed matrix-free CG | SPD operators with low-memory workspace | Existing |
| SciPy CSR / LinearOperator | Irregular or matrix-free operators; no densification | Integrated via solve_sparse |
| Numba stencil | Repeated structured stencil operations; lazy compilation | Integrated, opt-in |
| BiCGSTAB then restarted GMRES | Nonsymmetric systems; residual verification and bounded Krylov basis | Integrated |
| Geometric multigrid | Structured isotropic elliptic PDE only initially | Research prototype, integration pending |
| Restarted Lanczos | Partial symmetric eigensystems via SciPy eigsh | Integration pending |
| Streaming and chunked disk output | Large field postprocessing | Streaming norms existing; disk integration pending |
| Tensor-product sum factorization | High-order tensor elements | Research prototype; FEA integration pending |
| Mixed precision | Residual monitoring, conditioning safeguards and FP64 fallback required | Experimental only |
| AMR | Error-indicator driven; conservation and mesh checks required | Domain-specific research |
| AMG, IC, JFNK, ROM, checkpointing | Require representative workloads and cost/accuracy gates | Deferred |

## First integration

solve_sparse accepts real SciPy sparse matrices or LinearOperator instances. The caller declares SPD to choose CG; otherwise use BiCGSTAB, then GMRES on failure. Each method has its own iteration limit. A GMRES basis budget caps (restart+1)*n*8 bytes of basis payload, not other arrays, backend overhead or RSS. If no restart fits, return failure without fallback. Recompute the residual using the original operator; no claim about physical accuracy or forward error solely from residual. Input operator must be fixed and finite. Current implementation does not automatically choose between CSR and matrix-free or enforce a global memory budget. No preconditioner option in this adapter yet. For extreme scales, norm arithmetic may overflow or underflow.

poisson_operator implements the unscaled homogeneous Dirichlet five-point stencil on an equal-spacing rectangular interior grid; caller scales source by h^2. Numba is optional and compilation occurs on first application. Matrix products return fresh output arrays to comply with SciPy interface expectations.

Local test subset: 50 passed (45 earlier and five new cases), Python sandbox with NumPy 2.3.5, SciPy 1.17.0, Numba 0.65.1. Test cases compare against an independent sparse stencil, check SPD solve, a known BiCGSTAB breakdown and GMRES recovery, budget-limited failure, invalid input and both stencil backends. Full remote CI pending. 65,536 entries, seed 42, five warm calls median, single-thread BLAS: Python 36.083 ms, JIT 0.070607 ms, first compiled application 306.633 ms; maximum absolute output difference 0. This is stencil-only, not whole-solver speed. No claim of peak RSS improvement in this integration batch.

References: SciPy CG, BiCGSTAB and GMRES API documentation (https://docs.scipy.org/doc/scipy/reference/sparse.linalg.html); Lam et al., Numba: A LLVM-Based Python JIT Compiler (2015), DOI 10.1145/2833157.2833162; Barrett et al., Templates for the Solution of Linear Systems (https://www.netlib.org/templates/). Prior sandbox research supports the candidate list but does not establish production readiness.

Next: integrate geometric multigrid on its verified grid family, residual-checked partial eigenpairs, chunked streaming, and domain-appropriate tensor kernels, each with independent tests. Keep base and accelerated CI separate.
