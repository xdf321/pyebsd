import os
import sys
import time

import numpy as np
import matplotlib.pyplot as plt

import pyebsd


def xyz(tx, ty, tz):
    Rx = np.ndarray((3, 3))
    Ry = np.ndarray((3, 3))
    Rz = np.ndarray((3, 3))

    Rx[0] = [1, 0, 0]
    Rx[2] = [0, np.cos(tx), -np.sin(tx)]
    Rx[1] = [0, np.sin(tx), np.cos(tx)]

    Ry[0] = [np.cos(ty), 0, np.sin(ty)]
    Ry[1] = [0, 1, 0]
    Ry[2] = [-np.sin(ty), 0, np.cos(ty)]

    Rz[0] = [np.cos(tz), -np.sin(tz), 0]
    Rz[1] = [np.sin(tz), np.cos(tz), 0]
    Rz[2] = [0, 0, 1]

    R = np.dot(Ry, Rx)
    R = np.dot(Rz, R)

    return R


if __name__ == '__main__':
    t = np.linspace(-10, 10, 5)
    t = np.radians(t)
    theta, phi, psi = np.meshgrid(t, t, t)
    theta, phi, psi = np.radians(theta.ravel()), np.radians(
        phi.ravel()), np.radians(psi.ravel())

    A = np.ndarray((len(theta), 3, 3))
    i = 0
    for theta in t:
        for phi in t:
            for psi in t:
                A[i] = xyz(theta, phi, psi)
                i += 1

    pyebsd.plot_PF(R=A, ms=5)
    plt.show()

    # fname = os.path.join(pyebsd.DIR, 'data', 'QP170-375-15_cropped.ang')
    # scan = pyebsd.load_scandata(fname)
