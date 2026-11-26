import math
import pytest
from veritas.math import poisson_1d, heat_1d


def test_poisson_quadratic():
    x,u=poisson_1d(lambda x:2, cells=20, left=1,right=3)
    assert u==pytest.approx([1+3*t-t*t for t in x],abs=1e-12)
    assert poisson_1d(lambda x:2,cells=2,left=1,right=3)[1]==pytest.approx([1,2.25,3])


def test_poisson_order():
    def error(n):
        x,u=poisson_1d(lambda t:math.pi**2*math.sin(math.pi*t),cells=n)
        return max(abs(v-math.sin(math.pi*t)) for t,v in zip(x,u))
    assert error(20)/error(40)==pytest.approx(4,rel=.01)


@pytest.mark.parametrize('method',['explicit','backward_euler','crank_nicolson'])
def test_heat_mode(method):
    r=heat_1d(lambda x:math.sin(math.pi*x),diffusivity=.1,duration=.1,
              cells=20,steps=100,method=method,store_every=100)
    assert len(r.u)==2 and r.t==(0,.1)
    assert r.u[-1]==pytest.approx([math.exp(-.1*.1*math.pi**2)*math.sin(math.pi*x) for x in r.x],abs=.0003)


@pytest.mark.parametrize('method',['explicit','backward_euler','crank_nicolson'])
def test_steady_linear(method):
    r=heat_1d(lambda x:2+3*x,diffusivity=.1,duration=.05,cells=10,
              steps=10,left=2,right=5,method=method,store_every=3)
    assert len(r.u)==5 and r.t[-1]==.05
    for state in r.u:
        assert state==pytest.approx([2+3*x for x in r.x],abs=1e-12)


def test_one_interior_and_retention():
    kw=dict(diffusivity=.1,duration=.1,cells=2,steps=7,left=2,right=4)
    full=heat_1d(lambda x:0,**kw)
    thin=heat_1d(lambda x:0,**kw,store_every=3)
    assert thin.u==tuple(full.u[i] for i in (0,3,6,7))
    assert thin.u[-1][1]>0


def test_stability_and_validation():
    with pytest.raises(ValueError): heat_1d(lambda x:x,diffusivity=1,duration=1,cells=10,steps=1,method='explicit')
    with pytest.raises(ValueError): heat_1d(lambda x:x,diffusivity=0,duration=1)
    with pytest.raises(ValueError): poisson_1d(lambda x:0,cells=1)
    with pytest.raises(ValueError): heat_1d(lambda x:x,diffusivity=1,duration=1,store_every=0)
