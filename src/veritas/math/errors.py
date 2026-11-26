"""Error norms on paired finite samples (not spatially weighted integrals)."""
from dataclasses import dataclass
from math import fsum,hypot,sqrt
from ._validation import finite

@dataclass(frozen=True)
class ErrorNorms:
    count: int
    l1: float
    l2: float
    linf: float
    mae: float
    rmse: float
    relative_l2: float | None

def error_norms(observed,reference):
    """Unweighted discrete norms; relative L2 is undefined for zero reference."""
    a=tuple(finite(x,"observed") for x in observed)
    b=tuple(finite(x,"reference") for x in reference)
    if not a or len(a)!=len(b):
        raise ValueError("Expected equal nonempty sample arrays")
    e=tuple(finite(x-y,"error") for x,y in zip(a,b))
    n=len(e)
    l1=finite(fsum(map(abs,e)),"L1")
    l2=finite(hypot(*e),"L2")
    ref=finite(hypot(*b),"reference L2")
    return ErrorNorms(n,l1,l2,max(map(abs,e)),l1/n,l2/sqrt(n),
                      finite(l2/ref,"relative L2") if ref else None)
