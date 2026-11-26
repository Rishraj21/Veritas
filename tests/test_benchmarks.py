from math import pi, exp, sqrt, tanh
import pytest
from physcheck import BENCHMARKS, reference, check, CheckError, estimate_order

# Independent hand-evaluable cases; no expected results obtained from the implementation.
CASES = [
    ('pipe_flow', dict(pressure_drop=8, radius=1, viscosity=1, length=1), pi),
    ('couette_flow', dict(wall_speed=8, gap=2, y=.5), 2),
    ('plane_poiseuille', dict(pressure_gradient=4, gap=2, viscosity=2, y=1), 1),
    ('axial_bar', dict(force=1200, length=2, area=.002, youngs_modulus=200e9), 6e-6),
    ('cantilever_tip', dict(force=300, length=2, youngs_modulus=200e9, second_moment=1e-6), .004),
    ('circular_shaft', dict(torque=pi/2, length=2, shear_modulus=4, radius=1), .5),
    ('slab_conduction', dict(conductivity=2, area=3, thickness=.1, hot_temperature=310, cold_temperature=300), 600),
    ('lumped_cooling', dict(initial_temperature=400, ambient_temperature=300, h=10, area=2, mass=2, specific_heat=100, time=10), 300+100/exp(1)),
    ('spring_mass', dict(stiffness=16*pi*pi, mass=1), 2),
    ('insulated_fin', dict(conductivity=2, area=.5, perimeter=1, h=1, length=1, base_temperature=310, ambient_temperature=300), 10*tanh(1)),
]

@pytest.mark.parametrize('name,parameters,expected', CASES)
def test_reference(name, parameters, expected):
    assert reference(name, parameters) == pytest.approx(expected, rel=1e-12)

@pytest.mark.parametrize('name,parameters,expected', CASES)
def test_pass(name, parameters, expected):
    assert check(name, parameters, expected*1.005, rtol=.01).passed

@pytest.mark.parametrize('name,parameters,expected', CASES)
def test_fail(name, parameters, expected):
    assert not check(name, parameters, expected*1.05, rtol=.01).passed

@pytest.mark.parametrize('speed,y,expected', [(3,0,0),(3,1,3),(-3,.5,-1.5),(0,.5,0)])
def test_couette_boundaries(speed,y,expected):
    assert reference('couette_flow',dict(wall_speed=speed,gap=1,y=y)) == expected

@pytest.mark.parametrize('params', [dict(wall_speed=1,gap=0,y=0),dict(wall_speed=1,gap=1,y=2),dict(wall_speed=1,gap=1,y=-1),dict(wall_speed=1,gap=1,y=float('nan')),dict(wall_speed=True,gap=1,y=0),dict(wall_speed=1,gap=1),dict(wall_speed=1,gap=1,y=0,extra=1)])
def test_bad_parameters(params):
    with pytest.raises(CheckError): check('couette_flow',params,0)

@pytest.mark.parametrize('kwargs', [dict(rtol=-1),dict(atol=-1),dict(rtol=float('inf')),dict(rtol=True)])
def test_bad_tolerances(kwargs):
    with pytest.raises(CheckError): check('spring_mass',dict(stiffness=1,mass=1),0,**kwargs)

@pytest.mark.parametrize('value', [float('inf'),float('nan'),True,'1',None])
def test_invalid_observed(value):
    with pytest.raises(CheckError): check('spring_mass',dict(stiffness=1,mass=1),value)

def test_zero_reference():
    p=dict(wall_speed=1,gap=1,y=0)
    r=check('couette_flow',p,.0001,atol=.0002)
    assert r.passed and r.relative_error is None
    assert not check('couette_flow',p,.0001).passed

def test_negative_reference():
    r=check('couette_flow',dict(wall_speed=-5,gap=1,y=1),-4.95,rtol=.02)
    assert r.passed and r.relative_error == pytest.approx(.01)

def test_full_benchmark_coverage():
    assert {x[0] for x in CASES} == set(BENCHMARKS)

def test_order_exact_second_order():
    r=estimate_order(1,.5,.25,5,2,1.25)
    assert r['observed_order']==pytest.approx(2)
    assert r['extrapolated_value']==pytest.approx(1)

@pytest.mark.parametrize('inputs',[(1,.5,.3,5,2,1),(1,.5,.25,1,2,1),(1,.5,.25,1,1,1),(1,.5,.25,1,2,4),(.5,1,.25,1,2,3)])
def test_invalid_convergence(inputs):
    with pytest.raises(ValueError): estimate_order(*inputs)
