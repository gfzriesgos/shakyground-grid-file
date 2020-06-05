valparaiso_updated_global_vs30.grd: lima_updated_global_vs30.grd
	./combine_grd_with_valparaiso.py
lima_updated_global_vs30.grd: global_vs30.grd
	./combine_grd_with_lima_data.py
global_vs30.grd: global_vs30_grd.zip
	unzip global_vs30_grd.zip
global_vs30_grd.zip:
	./download_global_grid.sh

