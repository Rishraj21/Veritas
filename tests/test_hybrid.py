import pytest
np = pytest.importorskip('numpy')
sp = pytest.importorskip('scipy.sparse')
from veritas.math.hybrid import solve_sparse, poisson_operator


def test_sparse_spd():
    a = sp.diags([[-1]*3,[4]*4,[-1]*3],[-1,0,1],format='csr',dtype=float)
    r = solve_sparse(a, a@np.ones(4), spd=True)
    assert r.converged and r.methods == ('cg',)
    assert np.allclose(r.solution, 1)


def test_breakdown_fallback_and_budget():
    a = sp.csr_matrix([[0.,1.],[1.,0.]])
    r = solve_sparse(a,[1.,0.])
    assert r.converged and r.methods == ('bicgstab','gmres')
    assert np.allclose(r.solution,[0,1])
    r = solve_sparse(a,[1.,0.],basis_budget_bytes=16)
    assert not r.converged and r.methods == ('bicgstab',)


@pytest.mark.parametrize('compiled',[False,True])
def test_stencil(compiled):
    if compiled: pytest.importorskip('numba')
    a = poisson_operator(9,7,compiled=compiled)
    x = np.arange(63,dtype=float)
    tx = sp.diags([-np.ones(8),2*np.ones(9),-np.ones(8)],[-1,0,1])
    ty = sp.diags([-np.ones(6),2*np.ones(7),-np.ones(6)],[-1,0,1])
    reference = sp.kronsum(tx,ty,format='csr')
    assert np.allclose(a@x,reference@x)
    r = solve_sparse(a,reference@x,spd=True,rtol=1e-11)
    assert r.converged and np.allclose(r.solution,x,atol=1e-8)


def test_invalid():
    a = sp.eye(2)
    with pytest.raises(TypeError): solve_sparse(np.eye(2),[1,2])
    with pytest.raises(ValueError): solve_sparse(a,[1,2j])
    with pytest.raises(ValueError): solve_sparse(a,[1])
    with pytest.raises(ValueError): poisson_operator(0,1)
