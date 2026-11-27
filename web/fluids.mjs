import {staticsModels} from './statics.mjs';
// Scalar SI models: no dependencies, no worker startup, O(1) workspace.
const finite=x=>{if(typeof x!=='number'||!Number.isFinite(x))throw Error('Expected finite number');return x;};
const pos=x=>{if(finite(x)<=0)throw Error('Expected positive number');return x;};
const nonneg=x=>{if(finite(x)<0)throw Error('Expected nonnegative number');return x;};
const gamma=(rho,g)=>finite(pos(rho)*pos(g));
const models=[
 ['density','Density','kg/m³','ρ = m / V',[['Mass','kg',2],['Volume','m³',.002]],(m,v)=>pos(m)/pos(v)],
 ['specific_volume','Specific volume','m³/kg','v = 1 / ρ',[['Density','kg/m³',1000]],r=>1/pos(r)],
 ['specific_weight','Specific weight','N/m³','γ = ρg',[['Density','kg/m³',1000],['Gravity','m/s²',9.80665]],gamma],
 ['specific_gravity','Specific gravity','1','SG = ρ / ρref',[['Density','kg/m³',850],['Reference density','kg/m³',1000]],(r,d)=>pos(r)/pos(d)],
 ['kinematic_viscosity','Kinematic viscosity','m²/s','ν = μ / ρ',[['Dynamic viscosity','Pa·s',.001],['Density','kg/m³',1000]],(m,r)=>pos(m)/pos(r)],
 ['shear_stress','Newtonian shear stress','Pa','τ = μ du/dy',[['Dynamic viscosity','Pa·s',.001],['Velocity gradient','1/s',-100]],(m,d)=>pos(m)*finite(d)],
 ['compressibility','Compressibility','1/Pa','κ = 1 / K',[['Bulk modulus','Pa',2.2e9]],k=>1/pos(k)],
 ['volume_strain','Linearized volume strain','1','ΔV/V ≈ −Δp/K',[['Pressure change','Pa',1e6],['Bulk modulus','Pa',2.2e9]],(p,k)=>-finite(p)/pos(k)],
 ['laplace_pressure','Laplace pressure jump','Pa','Δp = σ(1/R₁ + 1/R₂)',[['Surface tension','N/m',.072],['Signed curvature','1/m',2000]],(s,c)=>nonneg(s)*finite(c)],
 ['capillary_rise','Capillary rise / depression','m','h = 2σ cosθ / (r Δρ g)',[['Surface tension','N/m',.072],['Contact angle','rad',0],['Radius','m',.0005],['Density difference','kg/m³',1000],['Gravity','m/s²',9.80665]],(s,t,r,d,g)=>{if(finite(t)<0||t>Math.PI)throw Error('Angle must be in [0, π]');return 2*(nonneg(s)/pos(r))*Math.cos(t)/pos(d)/pos(g);}],
 ['hydrostatic_pressure','Hydrostatic pressure','Pa','p = p₀ + ρgh',[['Density','kg/m³',1000],['Depth','m',2],['Surface pressure','Pa',0],['Gravity','m/s²',9.80665]],(r,h,p,g)=>finite(p)+gamma(r,g)*nonneg(h)],
 ['pressure_head','Pressure head','m','h = p / (ρg)',[['Pressure','Pa',19613.3],['Density','kg/m³',1000],['Gravity','m/s²',9.80665]],(p,r,g)=>finite(p)/gamma(r,g)],
 ['buoyancy','Buoyant force','N','F = ρgV',[['Density','kg/m³',1000],['Displaced volume','m³',.01],['Gravity','m/s²',9.80665]],(r,v,g)=>gamma(r,g)*nonneg(v)]
,...staticsModels];
export const catalog=Object.freeze(models.map(([id,title,unit,formula,fields])=>Object.freeze({id,title,unit,formula,fields:Object.freeze(fields.map(f=>Object.freeze(f)))})));
const functions=new Map(models.map(([id,,,,fields,fn])=>[id,{n:fields.length,fn}]));
export function calculate(id,args){const m=functions.get(id);if(!m||!Array.isArray(args)||args.length!==m.n)throw Error('Unknown model or incorrect argument count');return finite(m.fn(...args));}
