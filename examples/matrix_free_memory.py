"""Reproducible packed matrix-free CG allocation comparison."""
from math import sin, cos, pi, sqrt, fsum
from time import perf_counter
import tracemalloc
from veritas.math.krylov import conjugate_gradient, PoissonStencil2D


def list_cg(a, b, rtol=1e-9):
    """Simple list-based comparison; same stencil, no preconditioning."""
    b=list(b); n=len(b); x=[0.]*n; r=b.copy(); p=r.copy(); q=[0.]*n
    rho=fsum(v*v for v in r); tol=rtol*sqrt(rho)
    for k in range(1,n+1):
        a(p,q)
        alpha=rho/fsum(u*v for u,v in zip(p,q))
        for i in range(n):
            x[i]+=alpha*p[i]; r[i]-=alpha*q[i]
        newrho=fsum(v*v for v in r)
        if sqrt(newrho)<=tol:
            a(x,q)
            residual=sqrt(fsum((v-w)**2 for v,w in zip(b,q)))
            if residual<=tol: return x,k,residual
            r=[v-w for v,w in zip(b,q)]; p=r.copy(); rho=fsum(v*v for v in r)
            continue
        beta=newrho/rho
        for i in range(n): p[i]=r[i]+beta*p[i]
        rho=newrho
    raise RuntimeError('Comparison did not converge')


def measure(fn):
    tracemalloc.start()
    try:
        t=perf_counter(); result=fn(); dt=perf_counter()-t
        _,peak=tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return result,dt,peak


def problem(n):
    a=PoissonStencil2D(n,n)
    def modes(i,j):
        return [sin(m*pi*(i+1)/(n+1))*sin(m*pi*(j+1)/(n+1)) for m in (1,3,7)]
    lambdas=[4-4*cos(m*pi/(n+1)) for m in (1,3,7)]
    exact=[sum(modes(i,j)) for j in range(n) for i in range(n)]
    rhs=[fsum(l*v for l,v in zip(lambdas,modes(i,j))) for j in range(n) for i in range(n)]
    return a,exact,rhs


if __name__=='__main__':
    for n in (32,100):
        a,exact,b=problem(n)
        (x,k,res),dt,peak=measure(lambda:list_cg(a,b))
        print('list',n*n,k,dt,peak,res,max(abs(u-v) for u,v in zip(x,exact)))
        del x
        r,dt,peak=measure(lambda:conjugate_gradient(a,b,rtol=1e-9))
        assert r.converged
        print('packed',n*n,r.iterations,dt,peak,r.residual_l2,max(abs(u-v) for u,v in zip(r.solution,exact)))
