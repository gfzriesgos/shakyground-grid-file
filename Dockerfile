FROM ubuntu:20.04

# for not having interaction on installation process
ENV DEBIAN_FRONTEND noninteractive

WORKDIR /root

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
        wget \
        unzip \
        python3 \
        python3-pip \
        python3-rtree \
        python3-pyproj \
        proj-bin \
        libproj-dev

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

RUN wget https://apps.usgs.gov/shakemap_geodata/vs30/global_vs30.grd && \
    python3 ./to_netcdf.py global_vs30.grd netcdf.grd && \
    python3 ./combine_grd_with_lima_data.py && \
    python3 ./combine_grd_with_valparaiso.py && \
    rm lima_updated_global_vs30.grd && \
    rm global_vs30.grd && \
    mkdir -p /usr/share/git/shakyground && \
    mv netcdf.grd /usr/share/git/shakyground/USGSSlopeBasedTopographyProxy.grd && \
    mv valparaiso_updated_global_vs30.grd /usr/share/git/shakyground/FromSeismogeotechnicsMicrozonation.grd
