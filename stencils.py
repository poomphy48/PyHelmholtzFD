import numpy as np
from scipy.sparse import csr_matrix

def generate_index(ix1, ix2, iy1, iy2, nx):

    idx_bd_corner = np.array([ix1+iy1*nx, ix2+iy1*nx, ix1+iy2*nx, ix2+iy2*nx])
    idx_bd_l = ix1 + nx*np.arange(iy1+1, iy2)
    idx_bd_r = ix2 + nx*np.arange(iy1+1, iy2)
    idx_bd_b = np.arange(ix1+1, ix2) + iy1*nx
    idx_bd_t = np.arange(ix1+1, ix2) + iy2*nx

    return idx_bd_corner, idx_bd_l, idx_bd_r, idx_bd_b, idx_bd_t

def laplace_stencil(order_type, idx_pos, nx):

    idx_pos: np.array
    nx: int

    npoint_hh = len(idx_pos)

    if order_type == '2nd-central':
        
        ncal = 5
        idx_stencil = np.array([0, -1, 1, -nx, nx]).astype(int)
        coeff = np.array([-4.0, 1.0, 1.0, 1.0, 1.0])

        idx_row = np.repeat(idx_pos, ncal)
        idx_col = idx_row + np.tile(idx_stencil, npoint_hh)
        val = np.tile(coeff, npoint_hh)        
        
    elif order_type == '4th-central':
        
        ncal = 9
        idx_stencil = np.array([0, -1, 1, -nx, nx, -2, 2, -2*nx, 2*nx]).astype(int)
        coeff = np.array([-5, 16/12, 16/12, 16/12, 16/12, -1/12, -1/12, -1/12, -1/12])

        idx_row = np.repeat(idx_pos, ncal)
        idx_col = idx_row + np.tile(idx_stencil, npoint_hh)
        val = np.tile(coeff, npoint_hh)
    
    elif order_type == '9point':
        
        ncal = 9
        idx_stencil = np.array([0, -1, 1, -nx, nx, -nx-1, -nx+1, nx-1, nx+1]).astype(int)
        coeff = np.array([-3, 1/2, 1/2, 1/2, 1/2, 1/4, 1/4, 1/4, 1/4])

        idx_row = np.repeat(idx_pos, ncal)
        idx_col = idx_row + np.tile(idx_stencil, npoint_hh)
        val = np.tile(coeff, npoint_hh)
    
    return idx_row, idx_col, val

def wavenumber_stencil(idx_pos, MatHH1D, gamma):

    idx_pos: np.array
    MatHH1D: np.array # size = nxHH*nyHH, n = nx*ny > nxHH*nyHH
    gamma: float
    
    idx_row = np.copy(idx_pos)
    idx_col = np.copy(idx_pos)
    val = (gamma**2)*np.copy(MatHH1D)    
    
    return idx_row, idx_col, val

def oneway_stencil(stencil_type, idx_pos, idx_shift, gamma, gamma0=-1):

    if stencil_type == 'side_1st_bw_2pt':
        
        idx_shift: int # idx_shift = -1 / 1 / -nx / nx
            
        c_ow = (1.0-1.0j*gamma)

        nb, npoint = 1, len(idx_pos)
        idx_nb = np.array([idx_shift]) 
        coeff = np.array([-1.0]) / c_ow

        idx_row = np.repeat(idx_pos, nb)
        idx_col = idx_row + np.tile(idx_nb, npoint)
        val = np.tile(coeff, npoint)

    elif stencil_type == 'corner_1st_bw_2pt':
        
        idx_shift: np.array # idx_shift = 1,nx / -1,nx / 1,-nx / -1,-nx
            
        c_ow = (2.0-2.0j*gamma)
        
        nb, npoint = 2, 1
        idx_nb = np.copy(idx_shift) 
        coeff = np.array([-1.0, -1.0]) / c_ow

        idx_row = np.repeat(idx_pos, nb)
        idx_col = idx_row + np.tile(idx_nb, npoint)
        val = np.tile(coeff, npoint)
        
    ##########################################################################    

    elif stencil_type == 'side_1st_bw_3pt':
        
        idx_shift: np.array # idx_shift = -1,-2 / 1,2 / -nx,-2*nx / nx,2*nx
            
        c_ow = (1.5-1.0j*gamma)

        nb, npoint = 2, len(idx_pos)
        idx_nb = np.copy(idx_shift) 
        coeff = np.array([-2.0, 0.5]) / c_ow

        idx_row = np.repeat(idx_pos, nb)
        idx_col = idx_row + np.tile(idx_nb, npoint)
        val = np.tile(coeff, npoint)

    elif stencil_type == 'corner_1st_bw_3pt':

        idx_shift: np.array # idx_shift = 1,2,nx,2*nx / -1,-2,nx,2*nx / 1,2,-nx,-2*nx / -1,-2,-nx,-2*nx
        
        c_ow = (3.0-2.0j*gamma)
        
        nb, npoint = 4, 1
        idx_nb = np.copy(idx_shift)
        coeff = np.array([-2.0, 0.5, -2.0, 0.5]) / c_ow

        idx_row = np.repeat(idx_pos, nb)
        idx_col = idx_row + np.tile(idx_nb, npoint)
        val = np.tile(coeff, npoint)           
            
    ##########################################################################
    
    elif stencil_type == 'side_2nd_bw_3pt':
        
        idx_shift: np.array # idx_shift = 1,-nx,nx / -1,-nx,nx / nx,-1,1 / -nx,-1,1
        
        s1, s2, s3 = 1, 1, 1 # not work --> (-1)11, 1(-1)1, 11(-1)
        c_ow = 1j*s1*gamma + s2*(gamma**2) - s3       

        nb, npoint = 3, len(idx_pos)
        idx_nb = np.copy(idx_shift) 
        coeff = np.array([-1j*s1*gamma, 0.5*s3, 0.5*s3]) / c_ow

        idx_row = np.repeat(idx_pos, nb)
        idx_col = idx_row + np.tile(idx_nb, npoint)
        val = np.tile(coeff, npoint)
        
    elif stencil_type == 'corner_2nd_bw_3pt':
        
        print(':)')
        
    ###########################################################################
    
    # The 2nd one-way wave equation with the 2nd accuracy of finite difference    
    
    elif stencil_type == 'side_2ndOW_bw_1stACC':
        
        idx_shift: np.array
        #                normal dev. | tangent dev.
        # idx_shift (L) =   1,     2 | -nx,  nx
        # idx_shift (R) =  -1,    -2 | -nx,  nx
        # idx_shift (B) =  nx,  2*nx |  -1,   1
        # idx_shift (T) = -nx, -2*nx |  -1,   1
        
        a0, a1, a2 = 1, -1, 0 # 1st order of acc.
        b0, b1 = -2, 1
        
        const_ow = 1j*gamma*a0 + 0.5*b0 + gamma**2
        
        nb, npoint = 4, len(idx_pos)
        idx_nb = np.copy(idx_shift) 
        coeff = np.array([1j*gamma*a1, 1j*gamma*a2, 0.5*b1, 0.5*b1]) / const_ow

        idx_row = np.repeat(idx_pos, nb)
        idx_col = idx_row + np.tile(idx_nb, npoint)
        val = np.tile(coeff, npoint)
        
    elif stencil_type == 'side_2ndOW_bw_2ndACC':
        
        idx_shift: np.array
        #                normal dev. | tangent dev.
        # idx_shift (L) =   1,     2 | -nx,  nx
        # idx_shift (R) =  -1,    -2 | -nx,  nx
        # idx_shift (B) =  nx,  2*nx |  -1,   1
        # idx_shift (T) = -nx, -2*nx |  -1,   1
        
        a0, a1, a2 = 3/2, -4/2, 1/2 # 2nd order of acc.
        b0, b1 = -2, 1
        
        const_ow = 1j*gamma*a0 + 0.5*b0 + gamma**2
        
        nb, npoint = 4, len(idx_pos)
        idx_nb = np.copy(idx_shift) 
        coeff = np.array([1j*gamma*a1, 1j*gamma*a2, 0.5*b1, 0.5*b1]) / const_ow

        idx_row = np.repeat(idx_pos, nb)
        idx_col = idx_row + np.tile(idx_nb, npoint)
        val = np.tile(coeff, npoint)
    
    elif stencil_type == 'corner_1stOW_2ndACC':
        
        idx_shift: np.array
        #                 x-normal dev. | y-normal dev.
        # idx_shift (BL) =   1,     2    |  nx,   2*nx
        # idx_shift (BR) =  -1,    -2    |  nx,   2*nx
        # idx_shift (TL) =   1,     2    | -nx,  -2*nx
        # idx_shift (TR) =  -1,    -2    | -nx,  -2*nx
        
        m = np.sqrt(2) # OW equation: (\partial_n - i*k0*m) u_sc = 0
        a0, a1, a2 = 3/2, -4/2, 1/2
        # a0, a1, a2 = 1, -1, 0
    
        const_ow = a0 + a0 - 1j*m*gamma
        
        nb, npoint = 4, 1
        idx_nb = np.copy(idx_shift) 
        coeff = np.array([a1, a2, a1, a2]) / const_ow

        idx_row = np.repeat(idx_pos, nb)
        idx_col = idx_row + np.tile(idx_nb, npoint)
        val = np.tile(coeff, npoint)
    
    return idx_row, idx_col, val