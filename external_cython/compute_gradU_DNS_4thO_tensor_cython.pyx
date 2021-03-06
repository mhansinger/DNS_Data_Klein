# CYTHON Version to compute velocity gradients

# use: cythonize -a -i compute_gradU_LES_4thO_cython.pyx

#import cython
import numpy as np
cimport numpy as np
cimport cython
from libc.math cimport sqrt
# from cython.parallel import prange

#################
# USE SINGLE PRECISSION (np.float32 and float in C) FOR SPEED UP
#################
DTYPE = np.float32
ctypedef np.float_t DTYPE_t


@cython.boundscheck(False)
@cython.wraparound(False)
# cpdef or cdef does not matter in speed tests
cpdef compute_gradU_DNS_4thO_tensor_cython(float[:, :, ::1] U_bar, float[:, :, ::1] V_bar, float[:, :, ::1] W_bar, int Nx, int Ny, int Nz, float delta_x):
    # '''
    # Compute the magnitude of the gradient of the DNS c-field, based on neighbour cells
    # 4th Order central differencing
    # :return: nothing
    # '''

    cdef float[:, :,::1] grad_U_x = np.zeros([Nx, Ny, Nz],dtype=DTYPE)  # set output array to zero
    cdef float[:, :,::1] grad_V_x = np.zeros([Nx, Ny, Nz],dtype=DTYPE)
    cdef float[:, :,::1] grad_W_x = np.zeros([Nx, Ny, Nz],dtype=DTYPE)

    cdef float[:, :,::1] grad_U_y = np.zeros([Nx, Ny, Nz],dtype=DTYPE)  # set output array to zero
    cdef float[:, :,::1] grad_V_y = np.zeros([Nx, Ny, Nz],dtype=DTYPE)
    cdef float[:, :,::1] grad_W_y = np.zeros([Nx, Ny, Nz],dtype=DTYPE)

    cdef float[:, :,::1] grad_U_z = np.zeros([Nx, Ny, Nz],dtype=DTYPE)  # set output array to zero
    cdef float[:, :,::1] grad_V_z = np.zeros([Nx, Ny, Nz],dtype=DTYPE)
    cdef float[:, :,::1] grad_W_z = np.zeros([Nx, Ny, Nz],dtype=DTYPE)

    # the indexes should be unsigned integers
    cdef unsigned int l, m, n

    print('Computing gradients of U_bar on DNS mesh 4th Order with Cython')

    # compute gradients from the boundaries away ...
    for l in range(2,Nx-2):
        for m in range(2,Ny-2):
            for n in range(2,Nz-2):
                grad_U_x[l,m,n] = (-U_bar[l+2, m, n] + 8*U_bar[l+1,m, n] - 8*U_bar[l-1,m, n] + U_bar[l-2, m, n])/(12 * delta_x)
                grad_U_y[l,m,n] = (-U_bar[l, m+2, n] + 8*U_bar[l,m+1, n] - 8*U_bar[l,m-1, n] + U_bar[l, m-2, n])/(12 * delta_x)
                grad_U_z[l,m,n] = (-U_bar[l, m, n+2] + 8*U_bar[l,m, n+1] - 8*U_bar[l,m, n-1] + U_bar[l, m, n-2])/(12 * delta_x)

                grad_V_x[l,m,n] = (-V_bar[l+2, m, n] + 8*V_bar[l+1,m, n] - 8*V_bar[l-1,m, n] + V_bar[l-2, m, n])/(12 * delta_x)
                grad_V_y[l,m,n] = (-V_bar[l, m+2, n] + 8*V_bar[l,m+1, n] - 8*V_bar[l,m-1, n] + V_bar[l, m-2, n])/(12 * delta_x)
                grad_V_z[l,m,n] = (-V_bar[l, m, n+2] + 8*V_bar[l,m, n+1] - 8*V_bar[l,m, n-1] + V_bar[l, m, n-2])/(12 * delta_x)

                grad_W_x[l,m,n] = (-W_bar[l+2, m, n] + 8*W_bar[l+1,m, n] - 8*W_bar[l-1,m, n] + W_bar[l-2, m, n])/(12 * delta_x)
                grad_W_y[l,m,n] = (-W_bar[l, m+2, n] + 8*W_bar[l,m+1, n] - 8*W_bar[l,m-1, n] + W_bar[l, m-2, n])/(12 * delta_x)
                grad_W_z[l,m,n] = (-W_bar[l, m, n+2] + 8*W_bar[l,m, n+1] - 8*W_bar[l,m, n-1] + W_bar[l, m, n-2])/(12 * delta_x)

                # # compute the magnitude of the gradient
                # this_magGrad_U = sqrt(this_U_gradX ** 2 + this_U_gradY ** 2 + this_U_gradZ ** 2)
                # this_magGrad_V = sqrt(this_V_gradX ** 2 + this_V_gradY ** 2 + this_V_gradZ ** 2)
                # this_magGrad_W = sqrt(this_W_gradX ** 2 + this_W_gradY ** 2 + this_W_gradZ ** 2)
                #
                # grad_U_bar[l, m, n] = this_magGrad_U
                # grad_V_bar[l, m, n] = this_magGrad_V
                # grad_W_bar[l, m, n] = this_magGrad_W

    return grad_U_x, grad_V_x, grad_W_x, grad_U_y, grad_V_y, grad_W_y, grad_U_z, grad_V_z, grad_W_z
