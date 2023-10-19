#!/bin/bash

set -ex

cd dandi_upload
docker build . -t magland/pc-dandi-upload
docker push magland/pc-dandi-upload
./generate_spec.sh
cd ..

cd kilosort2_5
docker build . -t magland/pc-kilosort2_5
docker push magland/pc-kilosort2_5
./generate_spec.sh
cd ..

cd kilosort3
docker build . -t magland/pc-kilosort3
docker push magland/pc-kilosort3
./generate_spec.sh
cd ..

cd mountainsort5
docker build . -t magland/pc-mountainsort5
docker push magland/pc-mountainsort5
./generate_spec.sh
cd ..

cd spike_sorting_utils
docker build . -t magland/pc-spike-sorting-utils
docker push magland/pc-spike-sorting-utils
./generate_spec.sh
cd ..