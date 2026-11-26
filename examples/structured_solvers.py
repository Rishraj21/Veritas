"""Compare structured algorithms against dense LU with measured peak allocations."""
from time import perf_counter
import tracemalloc
from veritas.math import Tridiagonal,stationary_solve,solve_linear

def measure(name,fn):
    tracemalloc.start()
    try:
        t=perf_counter(); x=fn(); elapsed=perf_counter()-t
        _,peak=tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    print(f"{name}: {elapsed:.6f} s, {peak} peak traced bytes")
    return x

if __name__=="__main__":
    n=100
    a=Tridiagonal([-1]*(n-1),[4]*n,[-1]*(n-1))
    b=a.matvec([1]*n)
    dense=lambda: [[4 if i==j else -1 if abs(i-j)==1 else 0 for j in range(n)] for i in range(n)]
    for name,fn in (
        ("dense LU",lambda:solve_linear(dense(),b).solution),
        ("Thomas",lambda:a.factor().solve(b)),
        ("Jacobi",lambda:stationary_solve(a,b,method="jacobi").solution),
        ("Gauss-Seidel",lambda:stationary_solve(a,b).solution)):
        x=measure(name,fn)
        print("  residual_inf:",a.residual_inf(x,b))
