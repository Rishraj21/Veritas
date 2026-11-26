from pathlib import Path
import runpy
import pytest

demo = runpy.run_path(str(Path(__file__).resolve().parents[1]/"examples"/"radial_fvm.py"))
solve = demo["solve_pipe"]
params = dict(radius=.001,length=1.,viscosity=.001,pressure_drop=1000.)

def test_independent_refinement():
    report = demo["run_demo"]()
    errors = [r["relative_error"] for r in report["results"]]
    assert all(a>b for a,b in zip(errors,errors[1:]))
    assert not report["results"][0]["passed"]
    assert report["results"][-1]["passed"]
    assert report["convergence"]["observed_order"] == pytest.approx(2,abs=.05)
    assert report["convergence"]["extrapolated_value"] == pytest.approx(
        report["results"][-1]["expected"],rel=1e-6)

def test_pressure_reversal_and_zero():
    q = solve(32,**params)
    assert solve(32,**{**params,"pressure_drop":-1000.}) == pytest.approx(-q)
    assert solve(32,**{**params,"pressure_drop":0.}) == 0

def test_invalid_grid():
    with pytest.raises(ValueError): solve(1,**params)
