import math
from array import array
import pytest
from veritas.math.krylov import conjugate_gradient, PoissonStencil2D


def test_spd():
    def a(x,o): o[0]=4*x[0]+x[1]; o[1]=x[0]+3*x[1]
    r=conjugate_gradient(a,[1,2])
    assert r.converged and list(r.solution)==pytest.approx([1/11,7/11])
    assert r.residual_l2<1e-8 and r.solution.readonly


def test_preconditioner():
    d=[1.,100.,10000.]
    def a(x,o):
        for i,v in enumerate(d): o[i]=v*x[i]
    r=conjugate_gradient(a,d,diagonal=d)
    assert r.converged and r.iterations==1 and list(r.solution)==pytest.approx([1]*3)
    assert conjugate_gradient(a,d,x0=[1]*3).iterations==0


def test_poisson_manufactured():
    nx,ny=12,9; a=PoissonStencil2D(nx,ny)
    x=[math.sin(math.pi*(i+1)/(nx+1))*math.sin(2*math.pi*(j+1)/(ny+1))
       for j in range(ny) for i in range(nx)]
    lam=4-2*math.cos(math.pi/(nx+1))-2*math.cos(2*math.pi/(ny+1))
    r=conjugate_gradient(a,(lam*v for v in x),rtol=1e-11)
    assert r.converged and list(r.solution)==pytest.approx(x,abs=1e-10)


def test_multi_iteration_and_true_residual():
    a=PoissonStencil2D(20,20); b=[1.]*400
    r=conjugate_gradient(a,b,rtol=1e-9)
    q=array('d',[0.])*400; a(r.solution,q)
    assert r.converged and r.iterations>1
    assert math.sqrt(sum((v-w)**2 for v,w in zip(b,q)))==pytest.approx(r.residual_l2)
    assert r.residual_l2<=1e-9*20


def test_zero_and_limit():
    a=PoissonStencil2D(3,3)
    assert conjugate_gradient(a,[0.]*9).iterations==0
    r=conjugate_gradient(a,[1.]*9,max_iter=1)
    assert not r.converged and r.reason=='iteration limit'


def test_nonpositive_curvature():
    def a(x,o): o[0]=-x[0]
    r=conjugate_gradient(a,[1])
    assert not r.converged and r.reason=='nonpositive curvature'


@pytest.mark.parametrize('kw',[{'diagonal':[0]},{'x0':[1,2]},{'max_iter':0},{'rtol':0}])
def test_invalid(kw):
    with pytest.raises(ValueError): conjugate_gradient(lambda x,o:None,[1],**kw)


def test_incomplete_operator():
    with pytest.raises(ValueError): conjugate_gradient(lambda x,o:None,[1])
