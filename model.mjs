export function calculate({lengths_m,masses_kg,angles_rad,payload_kg=0,com_fractions,gravity=9.81}){
 const finite=x=>typeof x==='number'&&Number.isFinite(x);
 if(![lengths_m,masses_kg,angles_rad].every(Array.isArray))throw Error('Lengths, masses and angles must be arrays.');
 const n=lengths_m.length;
 if(!n||n>100||masses_kg.length!==n||angles_rad.length!==n)throw Error('Provide matching arrays for 1 to 100 links.');
 const fractions=com_fractions??Array(n).fill(0.5);
 if(!Array.isArray(fractions)||fractions.length!==n||fractions.some(v=>!finite(v)||v<0||v>1))throw Error('Provide one COM fraction from 0 to 1 per link.');
 if(lengths_m.some(v=>!finite(v)||v<=0)||masses_kg.some(v=>!finite(v)||v<0)||angles_rad.some(v=>!finite(v))||!finite(payload_kg)||payload_kg<0||!finite(gravity)||gravity<=0)throw Error('Check positive lengths and gravity, nonnegative masses, and finite angles.');
 const joints=[[0,0]],centers=[];let angle=0;
 lengths_m.forEach((length,i)=>{angle+=angles_rad[i];const [x,y]=joints.at(-1),dx=length*Math.cos(angle),dy=length*Math.sin(angle);centers.push([x+fractions[i]*dx,y+fractions[i]*dy]);joints.push([x+dx,y+dy]);});
 const tip=joints.at(-1);
 const torque=joints.slice(0,-1).map((p,j)=>gravity*(masses_kg.slice(j).reduce((sum,m,k)=>sum+m*(centers[j+k][0]-p[0]),0)+payload_kg*(tip[0]-p[0])));
 const energy=gravity*(masses_kg.reduce((sum,m,k)=>sum+m*centers[k][1],0)+payload_kg*tip[1]);
 if([...joints.flat(),...centers.flat(),...torque,energy].some(v=>!Number.isFinite(v)))throw Error('Inputs exceed numerical range.');
 return {holding_torque_Nm:torque,joint_positions_m:joints,link_centers_m:centers,potential_energy_J:energy};
}
