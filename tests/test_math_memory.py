"""Regression checks for streaming and output retention."""
import math
import tracemalloc
import pytest
from veritas.math import trapezoidal,simpson,simpson38,error_norms,solve_ivp,solve_linear

@pytest.mark.parametrize("rule",[trapezoidal,simpson,simpson38])
def test_quadrature_memory(rule):
    tracemalloc.start()
    try:
        result=rule(lambda x:x,0,1,n=30000)
        _,peak=tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert result==pytest.approx(.5)
    assert peak<256*1024

def test_streaming_norms():
    n=30000
    tracemalloc.start()
    try:
        result=error_norms((1 for _ in range(n)),(0 for _ in range(n)))
        _,peak=tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert result.count==n and result.l1==n
    assert result.l2==pytest.approx(math.sqrt(n))
    assert peak<256*1024
    with pytest.raises(ValueError): error_norms(iter([1]),iter([1,2]))

def test_scaled_norms():
    result=error_norms(iter([1e200,1e200]),iter([0,0]))
    assert result.l2==pytest.approx(math.sqrt(2)*1e200)

@pytest.mark.parametrize("method",["euler","midpoint","heun","rk4"])
@pytest.mark.parametrize("span",[(0,1),(1,0)])
def test_ode_retention(method,span):
    full=solve_ivp(lambda t,y:y,span,1,n=19,method=method)
    thin=solve_ivp(lambda t,y:y,span,1,n=19,method=method,store_every=7)
    final=solve_ivp(lambda t,y:y,span,1,n=19,method=method,store_every=100)
    assert thin.t==tuple(full.t[i] for i in (0,7,14,19))
    assert thin.y==tuple(full.y[i] for i in (0,7,14,19))
    assert final.y==(full.y[0],full.y[-1])
    assert thin.evaluations==final.evaluations==full.evaluations

def test_condition_inverse_row_sums():
    r=solve_linear([[1,2],[3,4]],[3,7],condition=True)
    assert r.solution==pytest.approx((1,1))
    assert r.condition_inf==pytest.approx(21)
