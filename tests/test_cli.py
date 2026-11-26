import json
import pytest
from veritas.cli import main

CASE={'id':'demo','benchmark':'couette_flow','parameters':{'wall_speed':2,'gap':1,'y':.5},'observed':1}

@pytest.mark.parametrize('observed,exit_code',[(1,0),(1.5,1)])
def test_cli_json(tmp_path,capsys,observed,exit_code):
    path=tmp_path/'case.json'
    path.write_text(json.dumps([{**CASE,'observed':observed}]))
    assert main(['validate',str(path),'--json'])==exit_code
    r=json.loads(capsys.readouterr().out)
    assert r['total']==1 and r['passed']==int(exit_code==0)

@pytest.mark.parametrize('text',['[]','{}','{bad','{"a": NaN}','{"a":1,"a":2}',json.dumps({**CASE,'unknown':1}),json.dumps({**CASE,'benchmark':None})])
def test_cli_invalid(tmp_path,capsys,text):
    p=tmp_path/'case.json';p.write_text(text)
    assert main(['validate',str(p)])==2
    assert 'veritas:' in capsys.readouterr().err

def test_cli_list(capsys):
    assert main(['list'])==0
    assert 'cantilever_tip' in capsys.readouterr().out

def test_cli_describe(capsys):
    assert main(['describe','pipe_flow'])==0
    assert 'Assumptions' in capsys.readouterr().out
