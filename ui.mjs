import {calculate} from './model.mjs';
const form=document.getElementById('torque-form'),out=document.getElementById('torque-result');
function list(id){const parts=document.getElementById(id).value.split(',');if(parts.some(v=>!v.trim()))throw Error('Use comma-separated numbers without empty entries.');return parts.map(Number);}
function update(event){
 event?.preventDefault();
 try{
  const payload=document.getElementById('payload').value;if(!payload.trim())throw Error('Enter a payload mass, including zero if there is none.');
  const r=calculate({lengths_m:list('lengths'),masses_kg:list('masses'),angles_rad:list('angles').map(v=>v*Math.PI/180),payload_kg:Number(payload)});
  out.replaceChildren();
  for(const [i,value] of r.holding_torque_Nm.entries()){const p=document.createElement('p');p.textContent=`Joint ${i+1} holding torque: ${value.toFixed(4)} N m`;out.append(p);}
  const p=document.createElement('p');p.textContent=`Potential energy: ${r.potential_energy_J.toFixed(4)} J`;out.append(p);
 }catch(error){out.textContent=error.message;}
}
form.addEventListener('input',()=>{out.textContent='Inputs changed. Calculate again to update the result.';});
form.addEventListener('submit',update);update();
