FROM ubuntu:18.04

WORKDIR /root

RUN apt-get update && \
    apt-get install -y \
    wget \
    unzip \
    python3 \
    python3-pip \
    python3-rtree

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

RUN wget https://earthquake.usgs.gov/static/lfs/data/global_vs30_grd.zip && \
    unzip global_vs30_grd.zip && \
    rm global_vs30_grd.zip && \
    python3 ./combine_grd_with_lima_data.py && \
    python3 ./combine_grd_with_valparaiso.py && \
    rm lima_updated_global_vs30.grd && \
    rm global_vs30.grd && \
    mkdir /usr/share/git/shakyground && \
    mv valparaiso_updated_global_vs30.grd /usr/share/git/shakyground/global_vs30.grd
