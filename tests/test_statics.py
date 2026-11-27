import json
from pathlib import Path
import pytest
from veritas.fluids import statics as s

@pytest.mark.parametrize('name,args,expected',json.loads(Path(__file__).with_name('statics_cases.json').read_text()))
def test_cases(name,args,expected):
    assert getattr(s,name)(*args)==pytest.approx(expected,rel=1e-10,abs=1e-12)


def test_paths():
    a=s.pressure_path(iter([(1000,-2),(800,1)]),101325,10)
    assert a.delta==12000 and a.pressure==113325
    assert s.pressure_path([(800,-1),(1000,2)],a.pressure,10).pressure==101325
    assert s.pressure_path([(1,-1e16),(1,-1),(1,1e16)],0,1).delta==1
    assert s.pressure_path(((1000,0) for _ in range(100000))).delta==0


@pytest.mark.parametrize('call',[lambda:s.gas_pressure(1,2,287,1,-1),lambda:s.liquid_pressure_change(1,1,1,1),lambda:s.pressure_offset(0,1),lambda:s.floating_fraction(1100,1000),lambda:s.plane_moment(1,1,2),lambda:s.rotation_level_change(1,-1,2),lambda:s.pressure_path([(0,1)])])
def test_invalid(call):
    with pytest.raises(ValueError): call()
