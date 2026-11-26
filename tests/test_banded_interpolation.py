import pytest
from veritas.math import (Tridiagonal,stationary_solve,solve_linear,
                          LinearInterpolator,NewtonInterpolator)
from math import isfinite
import tracemalloc

@pytest.mark.parametrize("n",[1,2,7,40])
def test_banded_vs_dense(n):
    a=Tridiagonal([-1]*(n-1),[4]*n,[-.5]*(n-1))
    exact=tuple(i+1 for i in range(n))
    b=a.matvec(exact)
    f=a.factor()
    assert f.solve(b)==pytest.approx(exact)
    assert f.solve([0]*n)==(0,)*n
    dense=[[4 if j==i else -1 if j==i-1 else -.5 if j==i+1 else 0
            for j in range(n)] for i in range(n)]
    assert f.solve(b)==pytest.approx(solve_linear(dense,b).solution)

@pytest.mark.parametrize("method",["jacobi","gauss_seidel"])
def test_stationary(method):
    a=Tridiagonal([-1]*9,[4]*10,[-1]*9)
    b=a.matvec([1]*10)
    r=stationary_solve(a,b,method=method)
    assert r.converged and r.solution==pytest.approx([1]*10,abs=1e-7)
    assert r.residual_inf==a.residual_inf(r.solution,b)
    assert stationary_solve(a,b,method=method,x0=[1]*10).iterations==0

def test_stationary_failure():
    a=Tridiagonal([2],[1,1],[2])
    r=stationary_solve(a,[1,1],method="jacobi",max_iter=5)
    assert not r.converged and r.iterations==5
    with pytest.raises(ValueError): stationary_solve(Tridiagonal([], [0], []),[1])

def test_pivot_and_shape():
    with pytest.raises(ValueError): Tridiagonal([1],[1],[1])
    with pytest.raises(ValueError): Tridiagonal([1],[0,1],[1]).factor()
    with pytest.raises(ValueError): Tridiagonal([], [1], []).factor().solve([1,2])

def test_large_banded_memory():
    n=10000
    tracemalloc.start()
    try:
        a=Tridiagonal((-1 for _ in range(n-1)),(4 for _ in range(n)),(-1 for _ in range(n-1)))
        b=a.matvec([1]*n)
        x=a.factor().solve(b)
        _,peak=tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert x==pytest.approx([1]*n)
    assert peak<12*1024*1024

@pytest.mark.parametrize("cls",[LinearInterpolator,NewtonInterpolator])
def test_reuse(cls):
    xs=[0,1,2]; ys=[1,3,5]
    p=cls(xs,ys)
    xs[0]=99; ys[0]=99
    for x in (0,.25,1,1.75,2):
        assert p(x)==pytest.approx(1+2*x)
    with pytest.raises(ValueError): p(3)
    with pytest.raises(ValueError): cls([0,0],[1,2])

def test_extreme_linear_span():
    assert LinearInterpolator([-1e308,1e308],[0,2])(0)==1

def test_newton_polynomial():
    p=NewtonInterpolator([0,1,2,3],[1,2,9,28])
    assert p(1.5)==pytest.approx(4.375)
