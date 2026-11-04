import {test} from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import fs from 'node:fs';
import {calculate} from '../model.mjs';
test('known one-link gravity lever',()=>assert.ok(Math.abs(calculate({lengths_m:[0.4],masses_kg:[2],angles_rad:[0],payload_kg:1}).holding_torque_Nm[0]-7.848)<1e-12));
test('invalid array lengths and negative mass rejected',()=>{assert.throws(()=>calculate({lengths_m:[1,2],masses_kg:[1],angles_rad:[0]}));assert.throws(()=>calculate({lengths_m:[1],masses_kg:[-1],angles_rad:[0]}));});
test('browser model agrees with Python in all three examples',()=>{
 for(const name of ['horizontal','folded','vertical']){
  const filename=`examples/${name}.json`,config=JSON.parse(fs.readFileSync(filename,'utf8'));
  const py=JSON.parse(execFileSync(process.env.PYTHON_BIN||'python3',['main.py','--config',filename],{encoding:'utf8'}));
  const js=calculate(config);
  js.holding_torque_Nm.forEach((v,i)=>assert.ok(Math.abs(v-py.holding_torque_Nm[i])<1e-10));
  assert.ok(Math.abs(js.potential_energy_J-py.potential_energy_J)<1e-10);
 }
});
test('potential energy derivative matches browser holding torque',()=>{
 const base={lengths_m:[0.3,0.2,0.1],masses_kg:[1,0.5,0.2],angles_rad:[0.4,-0.7,1.2],payload_kg:0.4};
 const torque=calculate(base).holding_torque_Nm;
 torque.forEach((t,j)=>{const plus=structuredClone(base),minus=structuredClone(base);plus.angles_rad[j]+=1e-6;minus.angles_rad[j]-=1e-6;const slope=(calculate(plus).potential_energy_J-calculate(minus).potential_energy_J)/2e-6;assert.ok(Math.abs(t-slope)<1e-7)});
});
