import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';import {staticsModels,pressure_path} from '../web/statics.mjs';
const models=new Map(staticsModels.map(m=>[m[0],m[5]]));
const cases=JSON.parse(readFileSync(new URL('./statics_cases.json',import.meta.url),'utf8'));
for(const [id,args,e] of cases)test(id,()=>assert(Math.abs(models.get(id)(...args)-e)<=1e-12+Math.abs(e)*1e-10));
test('paths',()=>{const a=pressure_path([[1000,-2],[800,1]],101325,10);assert.deepEqual(a,{delta:12000,pressure:113325});assert.equal(pressure_path([[800,-1],[1000,2]],a.pressure,10).pressure,101325);assert.equal(pressure_path([[1,-1e16],[1,-1],[1,1e16]],0,1).delta,1);function* stream(){for(let i=0;i<100000;i++)yield [1000,0];}assert.equal(pressure_path(stream()).delta,0);});
test('invalid',()=>{for(const [id,args] of [['gas_pressure',[1,2,287,1,-1,9.81]],['liquid_pressure_change',[1,1,1,1]],['pressure_offset',[0,1]],['floating_fraction',[1100,1000]],['plane_moment',[1,1,2,9.81]],['rotation_level_change',[1,-1,2,9.81]]])assert.throws(()=>models.get(id)(...args));assert.throws(()=>pressure_path([[0,1]]));});
test('defaults',()=>{for(const m of staticsModels)assert(Number.isFinite(m[5](...m[4].map(v=>v[2]))));});
