#!/usr/bin/env python3

"""
Script to combine the vs grid with the lima data.

The aim here is to combine the points from the soil lima
data set with the existing vs grid.

The resolution of the existing vs grid should stay as it is.
Also we don't want to change the values in the sea.

We only want to change the values for the vs where we have
proper data in our local data set.
"""

import geopandas as gpd
import numpy as np
from scipy.spatial import cKDTree
from scipy.io.netcdf import netcdf_file

from grdhelper import write_grd


def main():
    lima_data = gpd.read_file('lima/Soil_Condition_Lima/Soil Condition.shp')
    # The only important things here are the following:
    # geometry
    # Vs30Lima2
    # for the vs30Lima2 we have two kind values that we are not interted in
    # -1 (which indicates a missing value)
    # 180.0 (which is the value in the sea)
    # all the rest we want to reuse
    lima_data_with_interesting_values = lima_data[(lima_data['Vs30Lima2'] != -1.0) & (lima_data['Vs30Lima2'] != 180.0)]
    lima_x = lima_data_with_interesting_values.geometry.x.values
    lima_y = lima_data_with_interesting_values.geometry.y.values
    lima_z = lima_data_with_interesting_values['Vs30Lima2'].values

    lima_bbox = lima_data_with_interesting_values.total_bounds
    # something like:
    # array([-78.2 , -13.99, -76.01, -10.01])
    lima_min_x, lima_min_y, lima_max_x, lima_max_y = lima_bbox

    # And we build the spatial index
    spatial_index = cKDTree(data=np.vstack([lima_x, lima_y]).T)

    grid_filename = 'global_vs30.grd'

    grd_file = netcdf_file(grid_filename, 'r')

    grd_x = grd_file.variables['x'][:]
    grd_y = grd_file.variables['y'][:]

    # We need this dataset in the memory as we want to change it
    grd_z = np.zeros((len(grd_y), len(grd_x)), dtype='float32')
    grd_z[:] = grd_file.variables['z'][:]

    diff_grd_x = np.diff(grd_x).mean()
    diff_grd_y = np.diff(grd_y).mean()

    # We search from the center of our cell
    # We want to incluce all of them that may can be in this cell
    # so the max x difference is diff_grd_x / 2.0
    # and the max y difference diff_grd_y / 2.0
    # and we want the euclidean distance from that
    # --> but this is a bit too less, so we try
    # the distance from the lower right corner of the cell
    # to the upper left one.
    # this way we can also include points that are a bit outside of
    # our raster cell
    max_search_dist = np.sqrt((diff_grd_x)**2.0 + (diff_grd_y)**2.0)

    # now we want the grid
    for x_idx, x_val in enumerate(grd_x):
        if lima_min_x <= x_val <= lima_max_x:
            for y_idx, y_val in enumerate(grd_y):
                if lima_min_y <= y_val <= lima_max_y:
                    # We search for multiple values
                    spatial_search = spatial_index.query([x_val, y_val], distance_upper_bound=max_search_dist, k=32)
                    spatial_idxs = []

                    for temp_idx in range(len(spatial_search[0])):
                        spatial_dist = spatial_search[0][temp_idx]
                        search_idx = spatial_search[1][temp_idx]
                        if np.isfinite(spatial_dist):
                            spatial_idxs.append(search_idx)

                    # if we still have one, then we can use the element
                    # and we can set our grd
                    if spatial_idxs:
                        search_idx = spatial_idxs[0]
                        lima_z_on_search = lima_z[search_idx]
                        grd_z[y_idx, x_idx] = lima_z_on_search

    output_file = 'lima_updated_global_vs30.grd'
    write_grd(grd_x, grd_y, grd_z, output_file)


if __name__ == '__main__':
    main()
