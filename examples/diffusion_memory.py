"""Reproduce the local heat-equation retention comparison."""
import math
import tracemalloc
from time import perf_counter
from veritas.math import heat_1d

if __name__=="__main__":
    for k in (1,200):
        tracemalloc.start()
        try:
            t=perf_counter()
            r=heat_1d(lambda x:math.sin(math.pi*x),diffusivity=.1,duration=.1,
                      cells=500,steps=200,store_every=k)
            elapsed=perf_counter()-t
            _,peak=tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        error=max(abs(v-math.exp(-.01*math.pi**2)*math.sin(math.pi*x))
                  for x,v in zip(r.x,r.u[-1]))
        print(f"store_every={k}, states={len(r.u)}, peak_bytes={peak}, seconds={elapsed:.6f}, max_error={error:.8g}")
