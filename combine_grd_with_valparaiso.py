#!/usr/bin/env python3

"""
Script to combine the vs grid (with lima update)
with the vs zones in valpariso.
"""

import collections

import numpy as np
import geopandas as gpd
import rtree
import netCDF4
from shapely.geometry import box

from grdhelper import write_grd


VsBounds = collections.namedtuple("VsBounds", "min max")


def main():
    valpariso_data = gpd.read_file(
        "valparaiso/Valparaiso_Seismic_Zonation/Zonificación_Sísmica.shp"
    )

    # Those are the worst case shear velocity (vs) values
    vs_by_zone = {
        "A": VsBounds(min=502, max=np.inf),
        "B": VsBounds(min=352, max=501),
        "C": VsBounds(min=182, max=351),
        "D": VsBounds(min=152, max=181),
        "E": VsBounds(min=0, max=151),
    }

    spatial_index = rtree.index.Index()

    for idx, row in valpariso_data.iterrows():
        spatial_index.insert(idx, row.geometry.bounds)

    (
        valp_min_x,
        valp_min_y,
        valp_max_x,
        valp_max_y,
    ) = valpariso_data.total_bounds

    grid_filename = "lima_updated_global_vs30.grd"
    grd_file = netCDF4.Dataset(grid_filename, "r")

    grd_x = grd_file.variables["x"][:]
    grd_y = grd_file.variables["y"][:]

    grd_z = np.zeros((len(grd_y), len(grd_x)), dtype="float32")
    grd_z[:] = grd_file.variables["z"][:]

    diff_grd_x = np.diff(grd_x).mean()
    diff_grd_y = np.diff(grd_y).mean()

    for x_idx, x_val in enumerate(grd_x):
        if valp_min_x <= x_val <= valp_max_x:
            for y_idx, y_val in enumerate(grd_y):
                if valp_min_y <= y_val <= valp_max_y:
                    # Ok, we are in the bbox
                    # so, lets check if we are in a polygon right now
                    search_left = x_val - diff_grd_x / 2.0
                    search_bottom = y_val - diff_grd_y / 2.0
                    search_right = x_val + diff_grd_x / 2.0
                    search_top = y_val + diff_grd_y / 2.0

                    cell = box(
                        maxx=search_right,
                        minx=search_left,
                        maxy=search_top,
                        miny=search_bottom,
                    )

                    search_results = list(
                        spatial_index.intersection(
                            (
                                search_left,
                                search_bottom,
                                search_right,
                                search_top,
                            )
                        )
                    )
                    # the search result that we have is just based on the
                    # bounding box; we also have to test that our cell is in
                    # the geometry (at least partly)
                    found_classes = set()
                    for idx in search_results:
                        if valpariso_data.iloc[idx].geometry.intersects(cell):
                            name = valpariso_data.iloc[idx].Name
                            if name is not None:
                                found_classes.add(name)

                    # Now is the processing based on the classes
                    # At the moment we just want to make sure that
                    # our resulting data follows the boundaries by the
                    # classification that was given
                    bound_min = None
                    bound_max = None

                    for seismic_class in found_classes:
                        if (
                            bound_min is None
                            or bound_min < vs_by_zone[seismic_class].min
                        ):
                            bound_min = vs_by_zone[seismic_class].min
                        if (
                            bound_max is None
                            or bound_max > vs_by_zone[seismic_class].max
                        ):
                            bound_max = vs_by_zone[seismic_class].max

                    if bound_min is None:
                        bound_min = np.inf * -1
                    if bound_max is None:
                        bound_max = np.inf

                    current_value = grd_z[y_idx, x_idx]

                    grd_z[y_idx, x_idx] = handle_value_with_bounds(
                        current_value, bound_min, bound_max
                    )

    output_file = "valparaiso_updated_global_vs30.grd"
    write_grd(grd_x, grd_y, grd_z, output_file)


def handle_value_with_bounds(current_value, bound_min, bound_max):
    """
    Handle the current value with its bounds from the zones.

    The first idea was to just check the limits.
    So something like:

    if current_value < bound_min:
        current_value = bound_min
    if current_value > bound_max:
        current_value = bound_max
    return current_value


    However, we now want to give back the values of the bound_max
    (as long as it is not inf).
    """
    if np.isfinite(bound_max):
        return bound_max
    else:
        return current_value


if __name__ == "__main__":
    main()
