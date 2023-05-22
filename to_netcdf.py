#!/usr/bin/env python3

import sys
import numpy as np
from grdhelper import write_grd
import h5py


def main():
    input_filename = sys.argv[1]
    output_filename = sys.argv[2]
    input_file = h5py.File(input_filename, "r")

    grd_x = input_file["lon"][:]
    grd_y = input_file["lat"][:]
    grd_z = np.zeros((len(grd_y), len(grd_x)), dtype="float32")
    grd_z[:] = input_file["z"][:]
    write_grd(grd_x, grd_y, grd_z, output_filename)


if __name__ == "__main__":
    main()
