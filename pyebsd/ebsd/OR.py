import sys
import time
import numpy as np

from .orientation import (list_cubic_family_directions,
                          list_cubic_symmetry_operators,
                          reduce_cubic_transformations, average_orientation,
                          rotation_matrix_to_euler_angles,
                          euler_angles_to_rotation_matrix)


__all__ = ['OR_exp', 'OR']


def OR_exp(M, ph, phdict=dict(parent=2, child=1), sel=None, **kwargs):
    """
    Calculates the accurate orientation relationship between parent
    and child phases.

    - Miyamoto, G., Takayama, N., & Furuhara, T. (2009). Accurate 
      measurement of the orientation relationship of lath martensite 
      and bainite by electron backscatter diffraction analysis. 
      Scripta Materialia, 60(12), 1113-1116.
      http://doi.org/10.1016/j.scriptamat.2009.02.053
    """
    t0 = time.time()
    verbose = kwargs.pop('verbose', True)
    if verbose:
        sys.stdout.write('Calculating variants... ')
        sys.stdout.flush()

    if isinstance(phdict, dict):
        prt, chd = phdict['parent'], phdict['child']
    else:
        prt, chd = phdict[0], phdict[1]

    if not isinstance(sel, np.ndarray):
        sel = np.ndarray(len(R), dtype=bool)
        sel[:] = True

    # Calculate average rotation matrix of parent phase
    M_prt = average_orientation(M, sel=sel & (ph == prt), verbose=False)
    # Rotation matrices of child phases
    M_chd = M[sel & (ph == chd)]

    N = len(M_chd)

    # Get symmetry matrices
    C = list_cubic_symmetry_operators()
    # T : ndarray shape(24, 3, 3)
    T = np.tensordot(C, M_prt, axes=[[-1], [-2]]).transpose([0, 2, 1])
    # U : ndarray shape(N, 24, 3, 3)
    U = np.tensordot(M_chd, T, axes=[[-1], [-2]]).transpose([0, 2, 1, 3])

    isel = np.ndarray((24, N), dtype=int)
    V_sel = np.ndarray((24, N, 3, 3))
    trmax = np.ndarray((24, N))

    # axes=[[-1],[-2]] also works
    VrefT = np.tensordot(C[0], U[0, 0], axes=1).T
    # This step is non vectorized to save memory
    for i in range(len(C)):
        V = np.tensordot(C[i], U, axes=[[-1], [-2]]).transpose([1, 2, 0, 3])
        D = np.tensordot(V, VrefT, axes=[[-1], [-2]])
        tr = np.trace(D, axis1=2, axis2=3)
        neg = tr < 0.
        tr[neg] = -tr[neg]
        V[neg] = -V[neg]

        isel[i] = np.argmax(tr, axis=1)
        trmax[i] = np.max(tr, axis=1)
        V_sel[i] = V[(list(range(N)), isel[i])]

    jsel = (np.argmax(trmax, axis=0), list(range(N)))
    isel = isel[jsel]
    tr = trmax[jsel]
    V = V_sel[jsel]

    phi1, Phi, phi2 = rotation_matrix_to_euler_angles(
        V_sel[jsel], avg=True, verbose=False, **kwargs)
    # Average OR matrix
    Vavg = euler_angles_to_rotation_matrix(phi1, Phi, phi2, verbose=False)

    if verbose:
        sys.stdout.write('{:.2f} s\n'.format(time.time() - t0))

    # Delete arrays
    del M_chd, T, U, D, V_sel

    # Return the OR matrices V for each pixel,
    # the average OR matrix Vavg, and the
    # rotation matrix of the parent phase
    return V, Vavg, M_prt, isel


def OR(ps=([1, 1, 1], [0, 1, 1]), ds=([0, 1, 1], [1, 1, 1]), **kwargs):
    """
    From the parallel planes (ps) and directions (ds) determine the 
    orientations matrices of the parent (M_prt) and child (M_chd) 
    phases. Having M_prt and M_chd, calculates all the transformation 
    matrices V (all the variants) of the orientation relationship
    between the two phases.
    """
    trunc = kwargs.pop('trunc', 1e-8)
    ps, ds = np.asarray(ps), np.asarray(ds)
    p_prt, d_prt = ps[0], ds[0]  # parent phase
    p_chd, d_chd = ps[1], ds[1]  # child phase

    C = list_cubic_symmetry_operators()

    # check variants normal to plane 'n'. Due to numerical truncation,
    # instead of choosing the variants 'd' based on np.dot(d,n) == 0,
    # a tolerance 'trunc' is set. i.e., the variants are chosen
    # according to the criteria np.abs(np.dot(d,n)) <= trunc (1e-8)
    ds = np.dot(C, d_prt)
    sel = np.abs(np.asarray([np.dot(p_prt, d) for d in ds])) <= trunc
    d_prt = ds[sel][0]

    ds = np.dot(C, d_chd)
    sel = np.abs(np.asarray([np.dot(p_chd, d) for d in ds])) <= trunc
    d_chd = ds[sel][0]

    R_prt = np.array([d_prt, -np.cross(d_prt, p_prt), p_prt])
    R_chd = np.array([d_chd, -np.cross(d_chd, p_chd), p_chd])

    R_prt = R_prt/np.linalg.norm(R_prt, axis=1).reshape(-1, 1)
    R_chd = R_chd/np.linalg.norm(R_chd, axis=1).reshape(-1, 1)

    V = np.dot(R_chd.T, R_prt)

    if not kwargs.pop('single', False):
        V = np.matmul(V, C.transpose(0, 2, 1))
        V = reduce_cubic_transformations(V)

    return V
