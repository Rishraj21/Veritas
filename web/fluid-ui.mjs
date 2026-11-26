import {catalog,calculate} from './fluids.mjs';
const select=document.getElementById('fluid-model'), fields=document.getElementById('fluid-fields'), output=document.getElementById('fluid-output');
for(const m of catalog){const opt=document.createElement('option');opt.value=m.id;opt.textContent=m.title;select.append(opt);}
function render(){const m=catalog.find(v=>v.id===select.value);fields.replaceChildren();document.getElementById('fluid-formula').textContent=m.formula;for(const [name,unit,value] of m.fields){const label=document.createElement('label');label.textContent=name+' ('+unit+') ';const input=document.createElement('input');input.type='number';input.step='any';input.required=true;input.value=value;label.append(input);fields.append(label);}output.textContent='Ready.';}
select.addEventListener('change',render);
document.getElementById('fluid-form').addEventListener('submit',e=>{e.preventDefault();try{const m=catalog.find(v=>v.id===select.value);const x=calculate(m.id,Array.from(fields.querySelectorAll('input'),v=>v.valueAsNumber));output.textContent=Number(x.toPrecision(10))+' '+m.unit;}catch(err){output.textContent=err.message;}});
render();
