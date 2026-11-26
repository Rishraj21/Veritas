"""Reproduce local adaptive step and output-retention measurements."""
from math import exp, sin, cos
from time import perf_counter
import tracemalloc
from veritas.math import rk23

if __name__=="__main__":
    for tol in (1e-3,1e-6,1e-9):
        r=rk23(lambda t,y:-2*y,(0,3),1,rtol=tol,atol=tol/1000,first_step=1)
        assert r.converged
        print(tol,r.accepted,r.rejected,r.evaluations,abs(r.y[-1]-exp(-6)))
    for k in (1,100000):
        tracemalloc.start()
        try:
            t=perf_counter()
            r=rk23(lambda t,y:(y[1],-y[0]),(0,100),(1,0),
                   rtol=1e-7,atol=1e-9,store_every=k)
            elapsed=perf_counter()-t
            _,peak=tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        assert r.converged
        error=max(abs(r.y[-1][0]-cos(100)),abs(r.y[-1][1]+sin(100)))
        print(k,len(r.t),peak,elapsed,r.accepted,r.rejected,r.evaluations,error)
