import math
import pytest
from veritas.math import lu_factor,solve_linear,solve_ivp,stability_factor,error_norms

def test_pivoted_factorization():
    a=[[0,2,1],[1,1,0],[2,0,1]]
    f=lu_factor(a)
    l,u=f.unpack()
    assert f.swaps>0
    for i in range(3):
        for j in range(3):
            assert sum(l[i][k]*u[k][j] for k in range(3))==pytest.approx(a[f.permutation[i]][j])
    assert f.solve([7,3,5])==pytest.approx([1,2,3])
    assert f.solve([0,0,0])==(0,0,0)
    assert a==[[0,2,1],[1,1,0],[2,0,1]]

def test_scaled_matrix():
    r=solve_linear([[1e-20,0],[0,1e20]],[1e-20,2e20],condition=True)
    assert r.solution==pytest.approx([1,2])
    assert r.condition_inf==pytest.approx(1e40)
    assert r.backward_error<1e-14

def test_condition_and_residual():
    r=solve_linear([[2,0],[0,8]],[6,16],condition=True)
    assert r.solution==(3,2)
    assert r.residual_inf==0 and r.backward_error==0
    assert r.condition_inf==4
    assert solve_linear([[2]],[0]).condition_inf is None

@pytest.mark.parametrize("a,b",[
    ([[1,2],[2,4]],[1,2]),([[0,0],[1,2]],[1,2]),
    ([[1,2]],[1]),([],[]),([[1]],[1,2]),([[float("inf")]],[1]),
    ([[1,1],[1,1+1e-15]],[1,1])
])
def test_invalid_linear(a,b):
    with pytest.raises(ValueError): solve_linear(a,b)

@pytest.mark.parametrize("method,order,stages",[
    ("euler",1,1),("midpoint",2,2),("heun",2,2),("rk4",4,4)
])
def test_ode_order(method,order,stages):
    a=solve_ivp(lambda t,y:y,(0,1),1,n=20,method=method)
    b=solve_ivp(lambda t,y:y,(0,1),1,n=40,method=method)
    e1=abs(a.y[-1]-math.e); e2=abs(b.y[-1]-math.e)
    assert e1/e2==pytest.approx(2**order,rel=.06)
    assert a.evaluations==20*stages
    assert a.t[0]==0 and a.t[-1]==1 and len(a.y)==21

def test_vector_oscillator():
    r=solve_ivp(lambda t,y:(y[1],-y[0]),(0,2*math.pi),(1,0),n=100)
    assert r.y[-1]==pytest.approx((1,0),abs=1e-5)

def test_reverse_time_and_zero_interval():
    r=solve_ivp(lambda t,y:2*t,(2,0),4,n=10)
    assert r.y[-1]==pytest.approx(0,abs=1e-12)
    r=solve_ivp(lambda t,y:1/0,(1,1),2)
    assert r.t==(1,) and r.y==(2,) and r.evaluations==0

@pytest.mark.parametrize("call",[
    lambda:solve_ivp(lambda t,y:y,(0,1),1,n=0),
    lambda:solve_ivp(lambda t,y:y,(0,1),1,method="bad"),
    lambda:solve_ivp(lambda t,y:(1,2),(0,1),(1,)),
    lambda:solve_ivp(lambda t,y:float("nan"),(0,1),1),
    lambda:solve_ivp(lambda t,y:y,(0,1),()),
])
def test_invalid_ode(call):
    with pytest.raises(ValueError): call()

def test_stability():
    assert stability_factor(-1,"euler")==0
    assert abs(stability_factor(-3,"euler"))>1
    assert stability_factor(-2,"rk4")==pytest.approx(1/3)
    assert abs(stability_factor(1j,"rk4"))<1
    with pytest.raises(ValueError): stability_factor(float("nan"))

def test_error_norms():
    e=error_norms([2,0,3],[1,2,3])
    assert e.count==3 and e.l1==3 and e.linf==2
    assert e.l2==pytest.approx(math.sqrt(5))
    assert e.rmse==pytest.approx(math.sqrt(5/3))
    assert e.mae==1 and e.relative_l2==pytest.approx(math.sqrt(5/14))
    assert error_norms([1],[0]).relative_l2 is None

@pytest.mark.parametrize("a,b",[([],[]),([1],[1,2]),([float("nan")],[1])])
def test_invalid_norms(a,b):
    with pytest.raises(ValueError): error_norms(a,b)
