import pytest
np=pytest.importorskip('numpy'); sp=pytest.importorskip('scipy.sparse')
from veritas.math.spectral import partial_eigenpairs

def test_partial_modes():
    n=32
    a=sp.diags([-np.ones(n-1),2*np.ones(n),-np.ones(n-1)],[-1,0,1],format='csr')
    r=partial_eigenpairs(a,4,tol=1e-10)
    assert r.converged
    assert np.allclose(r.values,2-2*np.cos(np.arange(1,5)*np.pi/(n+1)),atol=1e-10)
    assert np.max(r.relative_residuals)<1e-9

def test_basis_budget():
    with pytest.raises(ValueError): partial_eigenpairs(sp.eye(10),3,basis_budget_bytes=8*10*3)
