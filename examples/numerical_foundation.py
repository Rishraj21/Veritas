"""Small numerical examples with independent reference values."""
from math import exp
from veritas.math import solve_linear,solve_ivp,error_norms

if __name__=="__main__":
    result=solve_linear([[0,2],[1,3]],[4,7],condition=True)
    print("Linear solution:",result)
    for method in ("euler","midpoint","heun","rk4"):
        sol=solve_ivp(lambda t,y:-2*y,(0,1),1,n=20,method=method)
        error=error_norms(sol.y,[exp(-2*t) for t in sol.t])
        print(method,"final state:",sol.y[-1],"RMSE:",error.rmse)
