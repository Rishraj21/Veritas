"""Error norms on paired finite samples (not spatially weighted integrals)."""
from dataclasses import dataclass
from math import hypot,sqrt
from itertools import zip_longest
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
    # Consume each iterable once. Scaled hypot avoids squaring huge values.
    sentinel=object()
    n=0; l1=0.0; correction=0.0; l2=0.0; ref=0.0; linf=0.0
    for x,y in zip_longest(observed,reference,fillvalue=sentinel):
        if x is sentinel or y is sentinel:
            raise ValueError("Expected equal nonempty sample arrays")
        x=finite(x,"observed"); y=finite(y,"reference")
        err=abs(finite(x-y,"error"))
        n+=1
        term=err-correction
        total=finite(l1+term,"L1")
        correction=(total-l1)-term
        l1=total
        l2=hypot(l2,err)
        ref=hypot(ref,y)
        linf=max(linf,err)
    if not n:
        raise ValueError("Expected equal nonempty sample arrays")
    l2=finite(l2,"L2"); ref=finite(ref,"reference L2")
    return ErrorNorms(n,l1,l2,linf,l1/n,l2/sqrt(n),
                      finite(l2/ref,"relative L2") if ref else None)
