#!/usr/bin/env python3

import numpy as np
import netCDF4

def write_grd(x, y, z, filename):
    """
    Write the data to a gmt grd file.

    This is like the pyrocko.plot.gmtpy.savegrd function,
    but it uses the netCDF4 lib as this allows us to
    write that large files (which is possible with scipy.io.netcdf
    only with limits, as huge files are no valid gmt grd files anymore).

    I had some "fun" to realize the source of this problem.

    However for our global vs grid, we need this support for
    large files.
    
    We also follow to use float32 values for the grid as
    our input vs grid does.
    """
    with netCDF4.Dataset(filename, 'w') as nc:
        nc.Conventions = 'COARDS/CF-1.0'

        kx, ky = 'x', 'y'
        nx, ny = len(x), len(y)

        nc.createDimension(kx, nx)
        nc.createDimension(ky, ny)

        xvar = nc.createVariable(kx, 'd', (kx,))
        xvar.long_name = kx
        yvar = nc.createVariable(ky, 'd', (ky,))
        yvar.long_name = ky
        zvar = nc.createVariable('z', 'f', (ky, kx))

        xvar[:] = x.astype(np.float64)
        yvar[:] = y.astype(np.float64)
        zvar[:] = z.astype(np.float32)

