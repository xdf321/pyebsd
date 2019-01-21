import sys
import time
import numpy as np
from itertools import permutations


def list_cubic_symmetry_operators(**kwargs):
    """
    List symmetry matrices for cubic symmetry group 
    """
    axis = np.array([[1., 0., 0.],
                     # 2-fold on <100>
                     [1., 0., 0.],
                     [0., 1., 0.],
                     [0., 0., 1.],
                     # 4-fold on <100>
                     [1., 0., 0.],
                     [0., 1., 0.],
                     [0., 0., 1.],
                     [-1., 0., 0.],
                     [0., -1., 0.],
                     [0., 0., -1.],
                     # 2-fold on <110>
                     [1., 1., 0.],
                     [1., 0., 1.],
                     [0., 1., 1.],
                     [1., -1., 0.],
                     [-1., 0., 1.],
                     [0., 1., -1.],
                     # 3-fold on <111>
                     [1., 1., 1.],
                     [1., -1., 1.],
                     [-1., 1., 1.],
                     [-1., -1., 1.],
                     [1., 1., -1.],
                     [1., -1., -1.],
                     [-1., 1., -1.],
                     [-1., -1., -1.]])

    angle = np.array([0.,
                      # 2-fold on <100>
                      np.pi,
                      np.pi,
                      np.pi,
                      # 4-fold on <100>
                      np.pi/2.,
                      np.pi/2.,
                      np.pi/2.,
                      np.pi/2.,
                      np.pi/2.,
                      np.pi/2.,
                      # 2-fold on <110>
                      np.pi,
                      np.pi,
                      np.pi,
                      np.pi,
                      np.pi,
                      np.pi,
                      # 3-fold on <111>
                      np.pi*2./3.,
                      np.pi*2./3.,
                      np.pi*2./3.,
                      np.pi*2./3.,
                      np.pi*2./3.,
                      np.pi*2./3.,
                      np.pi*2./3.,
                      np.pi*2./3.])

    return rotation_matrices_from_axis_angles(axis, angle).round(0)


def list_cubic_family_directions(d):
    """
    List all the variants of a family of directions 'd'
    """
    C = list_cubic_symmetry_operators()
    var = set([tuple(v) for v in np.dot(C, d)])
    return np.asarray(list(var))


def stereographic_projection(d, norm=True, coord='cartesian'):
    """
    Returns the coordinates of the stereographic projection of a direction 'd'
    """
    d = np.asarray(d)
    ndim = d.ndim
    shp = d.shape

    if 3 not in shp:
        return

    if ndim == 1:
        d = d.reshape(3, 1)
    elif ndim == 2:
        if shp[0] != 3:
            d = d.transpose([1, 0])
    else:
        return

    if norm:
        d = d/np.linalg.norm(d, axis=0)

    c0, c1 = d[0]/(1.+d[2]), d[1]/(1.+d[2])

    if coord == 'polar':
        r = (c0**2. + c1**2.)**.5
        theta = np.arctan2(c1, c0)
        theta[theta < 0] = theta[theta < 0] + 2*np.pi
        c0, c1 = r, theta

    if ndim == 1:
        c0, c1 = np.float(c0), np.float(c1)

    return c0, c1


def projection_to_direction(xy):
    xy = np.asarray(xy)
    ndim = xy.ndim

    if ndim == 1:
        xy = xy.reshape(1, -1)

    x = xy[:, 0]
    y = xy[:, 1]

    uvw = np.ndarray((len(xy), 3))

    uvw[:, 2] = (1. - x**2. - y**2.)/(1. + x**2. + y**2.)
    uvw[:, 0] = x*(1. + uvw[:, 2])
    uvw[:, 1] = y*(1. + uvw[:, 2])

    if ndim == 1:
        uvw = uvw.ravel()
    # d = [c0*(1.+d2), c1*(1.+d2), d2]
    return uvw


def misorientation_two_rotations(A, B, out='deg', math='avg', **kwargs):
    """
    Calculates the misorientation between A e B
    """

    Adim, Bdim = np.ndim(A), np.ndim(B)

    if Bdim > Adim:
        A, B = B, A
        Adim, Bdim = Bdim, Adim
    if (Adim == 3) and (Bdim == 2):
        D = np.tensordot(A, B, axes=[[-1], [-2]])
        x = np.abs(np.trace(D, axis1=1, axis2=2))  # trace
        if out != 'tr':
            x = np.arccos((x-1.)/2.)  # mis x in radians
            if out == 'deg':
                x = np.degrees(x)  # mis x in degrees
        if math == 'avg':
            x = np.mean(x)
        elif math == 'min':
            x = np.min(x)
        elif math == 'max':
            x = np.max(x)
    elif (Adim == 3) and (Bdim == 3):
        if kwargs.pop('vectorized', True):
            D = np.tensordot(A, B, axes=[[-1], [-2]]).transpose([0, 2, 1, 3])
            x = np.abs(np.trace(D, axis1=2, axis2=3))  # trace
            if out != 'tr':
                x = np.arccos((x-1.)/2.)  # mis x in radians
                if out == 'deg':
                    x = np.degrees(x)  # mis x in degrees
            if math == 'avg':
                x = np.mean(x, axis=0)
            elif math == 'min':
                x = np.min(x, axis=0)
            elif math == 'max':
                x = np.max(x, axis=0)
        else:
            if math is not None:
                x = np.ndarray(len(B))
            else:
                x = np.ndarray((len(B), len(A)))
            for i in range(len(B)):
                D = np.tensordot(A, B[i], axes=[[-1], [-2]])
                y = np.abs(np.trace(D, axis1=1, axis2=2))  # trace
                if out != 'tr':
                    y = np.arccos((y-1.)/2.)  # mis x in radians
                    if out == 'deg':
                        y = np.degrees(y)  # mis x in degrees
                if math == 'avg':
                    x[i] = np.mean(y)
                elif math == 'min':
                    x[i] = np.min(y)
                elif math == 'max':
                    x[i] = np.max(y)
                else:
                    x[i] = y
        del D
    else:
        return
    return x


def reduce_cubic_transformations(V, trunc=1e-3):
    """
    Remove redudant transformations (rotations) and returns a reduced
    number of matrices.

    V : ndarray shape(N,3,3)
        List of N 3x3 arrays (matrices) representing crystal bases.
    trunc : float
        Maximum misorientation angle (deg) between two bases to consider
        them equivalent to each other.
        Default: 1e-3
    """
    # Convert trunc from angle in degrees to the domain of the trace values
    # [-3, 3]. Because trunc is very small, the new value of trunc is very
    # close to 3.
    trunc = 2.*np.cos(np.radians(trunc)) + 1.
    C = list_cubic_symmetry_operators()

    pairs = []
    N = len(V)
    for i in range(N):
        p = []
        U = np.dot(C, V[i])
        for j in range(i, N):
            tr = np.abs(np.trace(np.dot(U, V[j].T), axis1=1, axis2=2))
            # From the trace tr you can get the misorientation angle
            # The following "if" is equivalent to check if the misorientation
            # angle is less the angle "trunc"
            if tr.max() >= trunc:
                p.append(j)
        pairs.append(p)

    single = [p.pop() for p in pairs if len(p) == 1]
    Vprime = V[single]

    return Vprime


def minimize_disorientation(V, V0, **kwargs):
    """
    Calculates the orientation that truly minimizes the disorientation
    between the list of orientations V and a single orientation V0.
    """
    n = kwargs.pop('n', 5)  # grid size
    maxdev = kwargs.pop('maxdev', .25)  # maximum deviation
    it = kwargs.pop('it', 3)  # number of iterations
    verbose = kwargs.pop('verbose', False)
    plot = kwargs.pop('plot', False)
    if verbose:
        sys.stdout.write('\nMinimizing disorientation...\n')
    if plot:
        from .plotting import plot_PF
        axmin = plot_PF(M=V, ms=.5, c='k', verbose=False)
    for i in range(it):
        step = maxdev/n
        t = np.linspace(-maxdev, maxdev, n)
        theta, phi, psi = np.meshgrid(t, t, t)
        theta, phi, psi = np.radians(theta.ravel()), np.radians(
            phi.ravel()), np.radians(psi.ravel())
        A = rotation_matrices_from_euler_angles(
            theta, phi, psi, conv='xyz', verbose=False)
        B = misorientation_two_rotations(V, np.tensordot(A, V0,
                                                         axes=[[-1], [-2]]).transpose([0, 2, 1]),
                                         out='tr', **kwargs)
        imax = np.argmax(B)  # get index of maximum trace value
        if verbose:
            dth = np.degrees(np.arccos((np.trace(A[imax])-1.)/2.))
            sys.stdout.write('{:2d} : {:g}, {:g}, {:g}; mis = {:g} deg\n'.format(
                i+1, np.degrees(theta[imax]), np.degrees(phi[imax]), np.degrees(psi[imax]), dth))
        if plot:
            x, y = PF(R=np.dot(A, V0).transpose([0, 2, 1]))
            ordc = np.argsort(B)
            axmin.scatter(x[ordc].ravel(), y[ordc].ravel(), c=np.repeat(
                B[ordc], x.shape[1]), lw=0, s=30, marker='s')
            axmin.plot(x[imax].ravel(), y[imax].ravel(), 'kx', ms=10, mew=2)

        V0 = np.dot(A[imax], V0)
        maxdev /= n
    del A, B

    return V0


def rotation_matrices_from_euler_angles(phi1, Phi, phi2, conv='zxz', **kwargs):
    """
    Given 3 Euler angles, calculates matrix R that describes the
    transformation (rotation) from the crystal base to the mechanical
    coordinates of the EBSD system. If the Euler angles are provided 
    as a iterable of length N (numpy array, list, tuple), the output
    will be in the form of a 3D array with shape (N,3,3)

    Parameters:
    -----------
    phi1 : float or list, tuple, or array(N)
    Phi : float or list, tuple, or array(N)
    phi2 : float or list, tuple, or array(N)
        Euler angles

    conv : string (optional)
        Rotation convention
        Default: zxz (Bunge notation)

    **kwargs :
        verbose : boolean
            If True (default), print calculation time

    """
    t0 = time.time()
    verbose = kwargs.pop('verbose', True)
    if verbose:
        sys.stdout.write('Calculating rotation matrices... ')
        sys.stdout.flush()

    if np.ndim(phi1) == 0:
        N = 1
    else:
        phi1 = np.asarray(phi1)
        Phi = np.asarray(Phi)
        phi2 = np.asarray(phi2)
        if len(phi1) == len(Phi) and len(phi1) == len(phi2):
            N = len(phi1)
        else:
            raise Exception('Lengths of phi1, Phi, and phi2 differ')

    cphi1, sphi1 = np.cos(phi1), np.sin(phi1)
    cPhi, sPhi = np.cos(Phi), np.sin(Phi)
    cphi2, sphi2 = np.cos(phi2), np.sin(phi2)
    R = np.ndarray((N, 3, 3))

    conv = conv.lower()
    if conv == 'zxz':
        R[:, 0, 0] = cphi1*cphi2 - sphi1*cPhi*sphi2
        R[:, 0, 1] = -cphi1*sphi2 - sphi1*cPhi*cphi2
        R[:, 0, 2] = sphi1*sPhi
        R[:, 1, 0] = sphi1*cphi2 + cphi1*cPhi*sphi2
        R[:, 1, 1] = -sphi1*sphi2 + cphi1*cPhi*cphi2
        R[:, 1, 2] = -cphi1*sPhi
        R[:, 2, 0] = sPhi*sphi2
        R[:, 2, 1] = sPhi*cphi2
        R[:, 2, 2] = cPhi
    elif conv == 'xyz':
        R[:, 0, 0] = cPhi*cphi1
        R[:, 0, 1] = -cPhi*sphi1
        R[:, 0, 2] = sPhi
        R[:, 1, 0] = cphi2*sphi1 + sphi2*sPhi*cphi1
        R[:, 1, 1] = cphi2*cphi1 - sphi2*sPhi*sphi1
        R[:, 1, 2] = -sphi2*cPhi
        R[:, 2, 0] = sphi2*sphi1 - cphi2*sPhi*cphi1
        R[:, 2, 1] = sphi2*cphi1 + cphi2*sPhi*sphi1
        R[:, 2, 2] = cphi2*cPhi
    else:
        raise Exception('"{}" convention not supported'.format(conv))

    if np.ndim(phi1) == 0:
        R = R.reshape(3, 3)

    if verbose:
        sys.stdout.write('{:.2f} s\n'.format(time.time() - t0))

    return R


def euler_angles_from_rotation_matrices(R, conv='zxz', **kwargs):
    """
    Calculates the Euler angles in a given rotation convention from
    the transformation matrix R or a list of rotations matrices R.

    Parameters:
    -----------
    R : numpy array shape(3, 3) or shape(N, 3, 3)
        Rotation matrix or list or rotation matrices

    conv : string (optional)
        Rotation convention
        Default: zxz (Bunge notation)

    **kwargs :
        verbose : boolean
            If True (default), print calculation time
        avg : boolean
            If True, calculates the Euler angles corresponding to the
            average orientation.
            If False (default), simply calculates the Euler angles for
            each rotation matrix provided.

    """

    Rdim = np.ndim(R)
    if Rdim == 2:
        R = R.reshape(1, 3, 3)

    if not kwargs.pop('avg', False):
        t0 = time.time()
        verbose = kwargs.pop('verbose', True)
        if verbose:
            sys.stdout.write('Calculating Euler angles... ')
            sys.stdout.flush()

        Phi = np.arccos(R[:, 2, 2])
        sPhi = np.sin(Phi)
        cphi1, cphi2 = -R[:, 1, 2]/sPhi, R[:, 2, 1]/sPhi
        sphi1, sphi2 = R[:, 0, 2]/sPhi, R[:, 2, 0]/sPhi

        # arctan2 returns value in the range [-pi,pi].
        phi1, phi2 = np.arctan2(sphi1, cphi1), np.arctan2(sphi2, cphi2)
        neg1, neg2 = phi1 < 0, phi2 < 0
        if np.ndim(neg1) > 0:
            # phi1 and phi2 to range [0, 2pi]
            phi1[neg1] = phi1[neg1] + 2.*np.pi
            phi2[neg2] = phi2[neg2] + 2.*np.pi
        else:
            if neg1:
                phi1 += 2.*np.pi
            if neg2:
                phi2 += 2.*np.pi

        if Rdim == 2:
            phi1, Phi, phi2 = phi1[0], Phi[0], phi2[0]

        if verbose:
            sys.stdout.write('{:.2f} s\n'.format(time.time() - t0))
    else:
        Phi = np.arccos(np.mean(R[:, 2, 2]))
        sPhi = np.sin(Phi)
        cphi1, cphi2 = -np.mean(R[:, 1, 2])/sPhi, np.mean(R[:, 2, 1])/sPhi
        sphi1, sphi2 = np.mean(R[:, 0, 2])/sPhi, np.mean(R[:, 2, 0])/sPhi
        phi1, phi2 = np.arctan2(sphi1, cphi1), np.arctan2(sphi2, cphi2)
        R_avg = rotation_matrices_from_euler_angles(
            phi1, Phi, phi2, verbose=False)
        # n=kwargs.pop('n', 5), maxdev=kwargs.pop('maxdev', .25)
        R_avg = minimize_disorientation(R, R_avg, **kwargs)
        phi1, Phi, phi2 = euler_angles_from_rotation_matrices(
            R_avg)  # recursive

    return phi1, Phi, phi2


def rotation_matrices_from_axis_angles(axis, theta):
    theta_dim = np.ndim(theta)
    axis_dim = np.ndim(axis)

    if axis_dim != theta_dim + 1:
        raise Exception('Invalid shapes of theta or axis')

    if theta_dim == 0:
        theta = np.asarray(theta).reshape(-1)
        axis = np.asarray(axis).reshape(-1, 3)

    axis = axis/np.linalg.norm(axis, axis=1).reshape(-1, 1)

    N = len(theta)
    R = np.ndarray((N, 3, 3))

    ctheta = np.cos(theta)
    ctheta1 = 1 - ctheta
    stheta = np.sin(theta)

    R[:, 0, 0] = ctheta1*axis[:, 0]**2. + ctheta
    R[:, 0, 1] = ctheta1*axis[:, 0]*axis[:, 1] - axis[:, 2]*stheta
    R[:, 0, 2] = ctheta1*axis[:, 0]*axis[:, 2] + axis[:, 1]*stheta
    R[:, 1, 0] = ctheta1*axis[:, 1]*axis[:, 0] + axis[:, 2]*stheta
    R[:, 1, 1] = ctheta1*axis[:, 1]**2. + ctheta
    R[:, 1, 2] = ctheta1*axis[:, 1]*axis[:, 2] - axis[:, 0]*stheta
    R[:, 2, 0] = ctheta1*axis[:, 2]*axis[:, 0] - axis[:, 1]*stheta
    R[:, 2, 1] = ctheta1*axis[:, 2]*axis[:, 1] + axis[:, 0]*stheta
    R[:, 2, 2] = ctheta1*axis[:, 2]**2. + ctheta

    if theta_dim == 0:
        R = R.reshape(3, 3)

    return R


def IPF(R, d='ND'):
    """
    Calculates crystallographic direction parallel to the mechanical 
    direction d (mechanical coordinates of the EBSD system).

    Parameters
    ----------
    R : numpy ndarray shape(N,3,3)
        Rotation matrices describing the transformation from the crystal 
        coordinates to the mechanical coordinates
    d : list or array shape(3) or string
        Mechanical direction parallel to the desired crystallographic 
        direction.
        d can be provided as a string representing common reference 
        directions as follows:
          d = 'ND' (normal direction) -> d = [0, 0, 1]

    Returns
    -------
    uvw : crystallographic direction parallel to mechanical direction 'd'
        uvw = M.d = (R^T).d
    """
    if d == 'ND':
        d = [0, 0, 1]

    if np.ndim(R) == 2:
        R = R.reshape(1, 3, 3)

    M = R.transpose([0, 2, 1])  # M = R^T
    uvw = np.dot(M, d)  # dot product M.D
    uvw = uvw/np.linalg.norm(uvw, axis=1).reshape(-1, 1)  # normalize uvw
    return uvw


def PF(R, proj=[1, 0, 0], parent_or=None):
    """
    Parameters
    ----------
    R : numpy ndarray shape(N,3,3) or numpy array(3,3)
        Rotation matrices describing the transformation from the crystal 
        coordinates to the mechanical coordinates
    proj : list or array shape(3)
        Family of directions projected in the pole figure. Default is '100'
    parent_or : list or array shape(3,3)
        Rotation matrix describing the orientation of the parent phase in the pole
        figure. The columns of the matrix correspond to the directions parallel to 
        the axes of the pole figure.
    """
    if np.ndim(R) == 2:
        R = R.reshape(1, 3, 3)

    if isinstance(parent_or, (list, tuple, np.ndarray)):
        R_prime = parent_or/np.linalg.norm(parent_or, axis=0)
        R_prime = np.linalg.inv(R_prime)
        R = np.tensordot(R_prime, R, axes=[[-1], [-2]]).transpose([1, 0, 2])

    N = R.shape[0]
    var = list_cubic_family_directions(d=proj)
    nvar = len(var)
    norm = np.linalg.norm(proj)

    xp = np.ndarray((N, nvar))
    yp = np.ndarray((N, nvar))

    # dm : directions in the mechanical coordinates
    # ndarray shape(N,3,nvar)
    dm = np.tensordot(R, var.T, axes=[[-1], [-2]])/norm
    sgn = np.sign(dm[:, 2, :])  # ndarray shape(N, nvar)
    sgn[sgn == 0.] = 1.  # change behavior of np.sign to x = 0

    # coordinates in the stereographic projection
    xp = sgn*dm[:, 0, :]/(np.abs(dm[:, 2, :]) + 1.)
    yp = sgn*dm[:, 1, :]/(np.abs(dm[:, 2, :]) + 1.)

    return (xp, yp)


def tr2ang(tr):
    """
    Converts the trace of a orientation matrix to the misorientation angle
    """
    return np.degrees(np.arccos((tr-1.)/2.))


def avg_orientation(R, sel=None, **kwargs):
    """
    Average orientation
    """
    t0 = time.time()
    # verbose is pased to 'euler_angles_from_rotation_matrices', so use kwargs.get, not kwargs.pop
    verbose = kwargs.get('verbose', True)
    if verbose:
        sys.stdout.write('Calculating average orientation... ')
        sys.stdout.flush()

    if isinstance(sel, np.ndarray):
        R_sel = R[sel]
    else:
        R_sel = R
    # M = R^-1 = R^T
    M_sel = np.transpose(R_sel, axes=[0, 2, 1])

    N = len(M_sel)
    MrefT = M_sel[N//2].T
    C = list_cubic_symmetry_operators()

    # tr = np.ndarray((M_sel.shape[0], len(C)))
    # vectorized is passed to euler_angles_from_rotation_matrices, which in turn is passed
    # to minimize_disorientation, so use kwargs.get, not kwargs.pop
    if kwargs.get('vectorized', True):
        # 4 dimensional numpy narray(N,24,3,3)
        Mprime = np.tensordot(C, M_sel,
                              axes=[[-1], [-2]]).transpose([2, 0, 1, 3])
        # misorientation matrices D
        D = np.tensordot(Mprime, MrefT, axes=[[-1], [-2]])
        tr = np.trace(D, axis1=2, axis2=3)
        neg = tr < -1.
        tr[neg] = -tr[neg]
        Mprime[neg] = -Mprime[neg]
        M_sel = Mprime[(list(range(N)), np.argmax(tr, axis=1))]
        # Mprime = np.tensordot(M_sel, MrefT, axes=[[-1],[-2]])
        # for m in len(C):
        #     a, b = C[m].nonzero()
        #     tr[m] = np.einsum('ij,j->i', Mprime[:,a,b], C[m,a,b])
        # m = np.argmax(np.abs(tr), axis=1)
        # Mprime = np.sign(tr[m])*np.tensordot(C[m], M_sel)
    else:
        for i in range(N):
            Mprime = np.tensordot(C, M_sel[i], axes=[[-1], [-2]])
            D = np.tensordot(Mprime, MrefT, axes=[[-1], [-2]])
            tr = np.trace(D, axis1=1, axis2=2)
            neg = tr < 0.  # select negative traces
            tr[neg] = -tr[neg]
            Mprime[neg] = -Mprime[neg]
            M_sel[i] = Mprime[np.argmax(tr)]

    R_sel = np.transpose(M_sel, [0, 2, 1])
    phi1, Phi, phi2 = euler_angles_from_rotation_matrices(
        R_sel, avg=True, **kwargs)  # verbose=True
    R_avg = rotation_matrices_from_euler_angles(phi1, Phi, phi2, verbose=False)

    if verbose:
        sys.stdout.write('{:.2f} s\n'.format(time.time() - t0))

    del D, Mprime, M_sel
    return R_avg


def misorientation(M, neighbors, sel=None):
    nneighbors = neighbors.shape[1]
    N = len(M)
    C = list_cubic_symmetry_operators()
    tr = np.ndarray((N, nneighbors))
    tr.fill(-1)

    if not isinstance(sel, np.ndarray):
        sel = np.ndarray(M.shape[0], dtype=bool)
        sel.fill(True)

    t0 = time.time()
    for k in range(nneighbors):
        ok = (neighbors[:, k] > 0) & sel & sel[neighbors[:, k]]
        # np.matmul(M[neighbors[ok,k]], M[ok].transpose([0,2,1]))
        S = np.einsum('ijk,imk->ijm', M[neighbors[ok, k]], M[ok])
        for m in range(len(C)):
            a, b = C[m].nonzero()
            # Trace using Einsum. Equivalent to (S[:,a,b]*C[m,a,b]).sum(axis=1)
            T = np.abs(np.einsum('ij,j->i', S[:, a, b], C[m, a, b]))
            tr[ok, k] = np.max(np.vstack([tr[ok, k], T]), axis=0)
        print(k)
    del S, T

    print(time.time()-t0)

    tr[tr > 3.] = 3.

    return tr2ang(tr)

# The product of two 2D matrices (numpy ndarray shape(N,N)) can be calculated
# using the function 'numpy.dot'. In order to compute the matrix product of
# higher dimensions arrays, numpy.dot can also be used, but paying careful
# attention to the indices of the resulting matrix. Examples:
#     - A is ndarray shape(N,M,3,3) and B is ndarray shape(3,3):
#     np.dot(A,B)[i,j,k,m] = np.sum(A[i,j,:,k]*B[m,:])
#     np.dot(A,B) is ndarray shape(N,M,3,3)

#     - A is ndarray shape(N,3,3) and B is ndarray shape(M,3,3):
#     np.dot(A,B)[i,j,k,m] = np.sum(A[i,:,j]*B[k,m,:])
#
#     The result np.dot(A,B) is ndarray shape(N,3,M,3). It's more convenient to
#     express the result as ndarray shape(N,M,3,3). In order to obtain the
#     desired result, the 'transpose' function should be used. i.e.,
#     np.dot(A,B).transpose([0,2,1,3]) results in ndarray shape(N,M,3,3)

#     - A is ndarray shape(3,3) and B is ndarray shape(N,M,3,3):
#     np.dot(A,B)[i,j,k,m] = np.sum(A[:,i]*B[j,k,m,:])
#
#     np.dot(A,B) is ndarray shape(3,N,M,3). np.dot(A,B).transpose([1,2,0,3])
#     results in ndarray shape(N,M,3,3)

# 'numpy.dot' is a particular case of 'numpy.tensordot':
# np.dot(A,B) == np.tensordot(A, B, axes=[[-1],[-2]])

# numpy.tensordot is two times faster than numpy.dot

# http://docs.scipy.org/doc/numpy/reference/generated/numpy.matmul.html
# http://docs.scipy.org/doc/numpy/reference/generated/numpy.dot.html
# http://docs.scipy.org/doc/numpy/reference/generated/numpy.tensordot.html
