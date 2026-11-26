import json
import pytest
from veritas import check, reference, CheckError
from veritas.units import to_si
from veritas.inputs import read_csv
from veritas.cli import main

def q(value, unit):
    return {"value": value, "unit": unit}

@pytest.mark.parametrize("value,unit,target,expected", [
    (200,"GPa","Pa",2e11), (4,"mm","m",.004),
    (1e6,"mm^4","m^4",1e-6), (100,"cm^2","m^2",.01),
    (1,"cP","Pa s",.001), (60,"L/min","m^3/s",.001),
    (25,"degC","K",298.15), (32,"degF","K",273.15),
    (212,"degF","K",373.15), (60,"rpm","Hz",1),
    (1,"N/mm","N/m",1000), (2,"kJ/(kg K)","J/(kg K)",2000),
])
def test_conversion(value,unit,target,expected):
    assert to_si(q(value,unit),target)==pytest.approx(expected)

@pytest.mark.parametrize("bad", [q(1,"N"),q(1,"MM"),q(True,"mm"),
    q(float("inf"),"mm"),{"unit":"mm"},{"value":1,"unit":"mm","extra":0}])
def test_bad_conversion(bad):
    with pytest.raises(ValueError): to_si(bad,"m")

def test_beam_units():
    r=check("cantilever_tip",{"force":q(.3,"kN"),"length":q(2000,"mm"),
        "youngs_modulus":q(200,"GPa"),"second_moment":q(1e6,"mm^4")},q(4.01,"mm"))
    assert r.passed and r.expected==pytest.approx(.004)
    assert r.observed==pytest.approx(.00401)

def test_temperature_tolerance():
    assert to_si(q(1.8,"delta_degF"),"K",difference=True)==pytest.approx(1)
    with pytest.raises(ValueError): to_si(q(1,"degC"),"K",difference=True)
    p={"initial_temperature":q(20,"degC"),"ambient_temperature":q(0,"degC"),
       "h":10,"area":1,"mass":1,"specific_heat":100,"time":0}
    assert reference("lumped_cooling",p)==pytest.approx(293.15)
    assert check("lumped_cooling",p,q(20.5,"degC"),rtol=0,atol=q(1,"delta_degC")).passed
    with pytest.raises(CheckError):
        check("lumped_cooling",p,q(20.5,"degC"),atol=q(1,"degC"))

def test_dimensional_mismatch():
    with pytest.raises(CheckError):
        check("couette_flow",{"wall_speed":2,"gap":q(1,"Pa"),"y":0},0)

HEADER="id,benchmark,observed,observed_unit,param.wall_speed,param.gap,param.gap.unit,param.y,param.y.unit\n"
ROW="test,couette_flow,1,m/s,2,10,mm,5,mm\n"

def test_csv_cli(tmp_path,capsys):
    p=tmp_path/"data.csv";p.write_text(HEADER+ROW)
    assert read_csv(p)[0]["parameters"]["gap"]==q(10,"mm")
    assert main(["validate",str(p),"--json"])==0
    report=json.loads(capsys.readouterr().out)
    assert report["passed"]==1
    assert report["results"][0]["expected"]==pytest.approx(1)

@pytest.mark.parametrize("data", [
    "", "benchmark,benchmark,observed\n",
    HEADER, HEADER+ROW.replace("10,mm,5,mm","10,mm"),
    HEADER.replace("param.y.unit","garbage")+ROW,
    HEADER+ROW.replace("couette_flow","unknown"),
    HEADER+ROW.replace(",5,mm",",,mm"),
    HEADER.replace("param.y.unit","param.force")+ROW,
])
def test_malformed_csv(tmp_path,data):
    p=tmp_path/"bad.csv";p.write_text(data)
    with pytest.raises(ValueError): read_csv(p)
