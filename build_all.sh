#!/bin/bash

set -ex

cd dandi_upload
dendro make-app-spec-file --app-dir . --spec-output-file spec.json
docker build . -t magland/pc-dandi-upload
docker push magland/pc-dandi-upload
cd ..

cd kilosort2_5
dendro make-app-spec-file --app-dir . --spec-output-file spec.json
docker build . -t magland/pc-kilosort2_5
docker push magland/pc-kilosort2_5
cd ..

cd kilosort3
dendro make-app-spec-file --app-dir . --spec-output-file spec.json
docker build . -t magland/pc-kilosort3
docker push magland/pc-kilosort3
cd ..

cd mountainsort5
dendro make-app-spec-file --app-dir . --spec-output-file spec.json
docker build . -t magland/pc-mountainsort5
docker push magland/pc-mountainsort5
cd ..

cd spike_sorting_utils
dendro make-app-spec-file --app-dir . --spec-output-file spec.json
docker build . -t magland/pc-spike-sorting-utils
docker push magland/pc-spike-sorting-utils
cd ..