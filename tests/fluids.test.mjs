import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';import {calculate,catalog} from '../web/fluids.mjs';
const cases=JSON.parse(readFileSync(new URL('./fluid_cases.json',import.meta.url),'utf8'));
for(const [id,args,expected] of cases)test(id,()=>assert(Math.abs(calculate(id,args)-expected)<=1e-15+Math.abs(expected)*1e-12));
test('invalid',()=>{for(const [id,args] of [['density',[1,0]],['shear_stress',[-1,2]],['capillary_rise',[.07,4,.001,1000,9.81]],['hydrostatic_pressure',[1000,-1,0,9.81]],['density',[NaN,1]],['density',[true,1]]])assert.throws(()=>calculate(id,args));});
test('catalog defaults',()=>{for(const m of catalog)assert(Number.isFinite(calculate(m.id,m.fields.map(f=>f[2]))));});
