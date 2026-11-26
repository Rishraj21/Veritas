import math
import pytest
from veritas.math import (bisection,newton,secant,trapezoidal,midpoint,
                          simpson,simpson38,derivative,second_derivative,
                          linear_interpolate,newton_interpolate)

@pytest.mark.parametrize("solve", [
    lambda f: bisection(f,1,2),
    lambda f: newton(f,lambda x:2*x,1),
    lambda f: secant(f,1,2),
])
def test_roots(solve):
    r=solve(lambda x:x*x-2)
    assert r.converged and r.root==pytest.approx(math.sqrt(2),abs=1e-9)
    assert r.residual<=1e-10

def test_root_failure():
    assert not bisection(lambda x:x*x-2,1,2,max_iter=1).converged
    assert not newton(lambda x:x*x+1,lambda x:2*x,0).converged
    assert not secant(lambda x:x*x+1,-1,1).converged
    assert not bisection(lambda x:-1 if x<0 else 1,-1,1).converged

def test_root_endpoint():
    assert bisection(lambda x:x,0,1).iterations==0

@pytest.mark.parametrize("solve", [
    lambda: bisection(lambda x:x*x+1,-1,1),
    lambda: bisection(lambda x:x,2,1),
    lambda: newton(lambda x:float("nan"),lambda x:1,0),
    lambda: secant(lambda x:x,1,1),
    lambda: bisection(lambda x:x,-1,1,xtol=0),
])
def test_bad_roots(solve):
    with pytest.raises(ValueError): solve()

@pytest.mark.parametrize("rule,n",[(trapezoidal,100),(midpoint,100),(simpson,100),(simpson38,99)])
def test_integral(rule,n):
    assert rule(lambda x:2*x+3,0,2,n=n)==pytest.approx(10)
    assert rule(lambda x:2*x+3,2,0,n=n)==pytest.approx(-10)
    assert rule(lambda x:2*x+3,1,1,n=n)==0

@pytest.mark.parametrize("rule,n",[(simpson,10),(simpson38,12)])
def test_cubic(rule,n):
    assert rule(lambda x:x**3,0,1,n=n)==pytest.approx(.25,abs=1e-14)

@pytest.mark.parametrize("rule,ratio",[(trapezoidal,4),(midpoint,4),(simpson,16),(simpson38,16)])
def test_quadrature_convergence(rule,ratio):
    exact=math.e-1
    e1=abs(rule(math.exp,0,1,n=12)-exact)
    e2=abs(rule(math.exp,0,1,n=24)-exact)
    assert e1/e2==pytest.approx(ratio,rel=.03)

@pytest.mark.parametrize("rule,n",[(trapezoidal,0),(midpoint,True),(simpson,3),(simpson38,4)])
def test_bad_quadrature(rule,n):
    with pytest.raises(ValueError): rule(math.sin,0,1,n=n)

@pytest.mark.parametrize("method",["forward","backward","central"])
def test_derivative(method):
    assert derivative(lambda x:3*x+2,2,h=1e-3,method=method)==pytest.approx(3)
    assert derivative(math.sin,.4,h=1e-5,method=method)==pytest.approx(math.cos(.4),abs=3e-6)

def test_second_derivative():
    assert second_derivative(lambda x:3*x*x+2*x,1,h=.01)==pytest.approx(6,abs=1e-8)

@pytest.mark.parametrize("fn",[lambda:derivative(math.sin,1,h=0),
    lambda:derivative(math.sin,1,h=1e-30),lambda:derivative(math.sin,1,h=.1,method="bad"),
    lambda:second_derivative(math.sin,1,h=1e-30)])
def test_invalid_derivatives(fn):
    with pytest.raises(ValueError): fn()

@pytest.mark.parametrize("rule",[linear_interpolate,newton_interpolate])
def test_interpolation(rule):
    assert rule([0,1,3],[2,5,11],2)==pytest.approx(8)
    assert rule([0,1,3],[2,5,11],3)==11
    with pytest.raises(ValueError): rule([0,1,3],[2,5,11],4)
    with pytest.raises(ValueError): rule([0,0],[2,5],0)
    with pytest.raises(ValueError): rule([0,1],[2],0)

def test_polynomial():
    assert newton_interpolate([0,1,3],[0,1,9],2)==pytest.approx(4)
