"""Hosted CI browser smoke; serves actual ES modules over loopback."""
from pathlib import Path
from threading import Thread
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from playwright.sync_api import sync_playwright
import json, tempfile, struct

root=Path(__file__).resolve().parents[1]/'web'
server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(root)))
Thread(target=server.serve_forever,daemon=True).start()
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        page=browser.new_page()
        page.goto(f'http://127.0.0.1:{server.server_port}/')
        page.select_option('#fluid-model','density')
        page.locator('#fluid-form button').click()
        assert page.locator('#fluid-output').inner_text()=='1000 kg/m³'
        page.select_option('#fluid-model','hydrostatic_pressure')
        page.locator('#fluid-form button').click()
        assert page.locator('#fluid-output').inner_text()=='19613.3 Pa'
        page.select_option('#fluid-model','plane_force')
        page.locator('#fluid-form button').click()
        assert page.locator('#fluid-output').inner_text()=='177720 N'
        page.select_option('#fluid-model','floating_fraction')
        page.locator('#fluid-form button').click()
        assert page.locator('#fluid-output').inner_text()=='0.8 1'
        for method in ('multigrid','cg','wasm-cg'):
            page.select_option('#grid','63')
            page.select_option('#method',method)
            page.click('#run')
            page.wait_for_function("document.querySelector('#output').textContent.startsWith('{')")
            r=json.loads(page.locator('#output').inner_text())
            assert r['ok'] and r['converged'] and r['relativeResidual']<=1e-9,r
        with tempfile.NamedTemporaryFile(suffix='.bin') as f:
            f.write(struct.pack('<3d',3,4,12));f.flush()
            page.set_input_files('#file',f.name);page.click('#stream')
            page.wait_for_function("document.querySelector('#output').textContent.startsWith('{')")
            r=json.loads(page.locator('#output').inner_text())
            assert r['ok'] and r['norm']==13,r
        page.select_option('#grid','511')
        page.select_option('#method','cg')
        page.click('#run');page.click('#cancel')
        assert page.locator('#output').inner_text()=='Cancelled.'
        browser.close()
finally:
    server.shutdown()
