valparaiso_updated_global_vs30.grd: lima_updated_global_vs30.grd
	./combine_grd_with_valparaiso.py
lima_updated_global_vs30.grd: netcdf.grd
	./combine_grd_with_lima_data.py
netcdf.grd:
	./to_netcdf.py global_vs30.grd netcdf.grd
global_vs30.grd:
	./download_global_grid.sh

