import json
from pathlib import Path
import pytest
from veritas import fluids

CASES = json.loads(Path(__file__).with_name('fluid_cases.json').read_text())

@pytest.mark.parametrize('name,args,expected', CASES)
def test_reference(name, args, expected):
    assert getattr(fluids, name)(*args) == pytest.approx(expected, rel=1e-12, abs=1e-15)

@pytest.mark.parametrize('call', [lambda: fluids.density(1,0), lambda: fluids.shear_stress(-1,2), lambda: fluids.capillary_rise(.07,4,.001,1000), lambda: fluids.hydrostatic_pressure(1000,-1), lambda: fluids.density(float('nan'),1), lambda: fluids.density(True,1)])
def test_invalid(call):
    with pytest.raises(ValueError): call()
