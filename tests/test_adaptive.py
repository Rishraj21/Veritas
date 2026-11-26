import math
import pytest
from veritas.math.adaptive import rk23


def test_decay_and_accuracy():
    loose=rk23(lambda t,y:-2*y,(0,3),1,rtol=1e-3,atol=1e-6)
    tight=rk23(lambda t,y:-2*y,(0,3),1,rtol=1e-7,atol=1e-10)
    exact=math.exp(-6)
    assert loose.converged and tight.converged
    assert abs(tight.y[-1]-exact)<abs(loose.y[-1]-exact)
    assert tight.y[-1]==pytest.approx(exact,rel=3e-6)
    assert tight.accepted>loose.accepted
    assert tight.evaluations==1+3*(tight.accepted+tight.rejected)


def test_rejection_and_retention():
    kw=dict(first_step=1,rtol=1e-7,atol=1e-10)
    full=rk23(lambda t,y:y,(0,1),1,**kw)
    thin=rk23(lambda t,y:y,(0,1),1,store_every=100000,**kw)
    assert full.converged and full.rejected>0
    assert thin.t==(0,1) and thin.y==(full.y[0],full.y[-1])
    assert thin.evaluations==full.evaluations
    assert thin.y[-1]==pytest.approx(math.e,rel=1e-6)


def test_vector_and_reverse():
    r=rk23(lambda t,y:(y[1],-y[0]),(0,2*math.pi),(1,0),rtol=1e-8,atol=1e-10)
    assert r.converged and r.y[-1]==pytest.approx((1,0),abs=1e-7)
    r=rk23(lambda t,y:2*t,(2,0),4,max_step=.1)
    assert r.converged and r.t[-1]==0 and r.y[-1]==pytest.approx(0,abs=1e-12)


def test_limit_and_zero_interval():
    r=rk23(lambda t,y:y,(0,1),1,first_step=.01,max_attempts=1,store_every=100)
    assert not r.converged and r.reason=="attempt limit" and r.t[-1]<1
    r=rk23(lambda t,y:1/0,(1,1),2)
    assert r.converged and r.evaluations==0 and r.y==(2,)


@pytest.mark.parametrize('kwargs',[{'rtol':0},{'atol':-1},{'first_step':0},{'max_step':0},{'store_every':0},{'max_attempts':0}])
def test_invalid(kwargs):
    with pytest.raises(ValueError): rk23(lambda t,y:y,(0,1),1,**kwargs)


def test_dimension_and_nonfinite():
    with pytest.raises(ValueError): rk23(lambda t,y:(1,2),(0,1),(1,))
    with pytest.raises(ValueError): rk23(lambda t,y:float('nan'),(0,1),1)
