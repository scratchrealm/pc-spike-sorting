#!/bin/bash

set -ex

cd dandi_upload
docker build . -t magland/pc-dandi-upload
docker push magland/pc-dandi-upload
protocaas make-app-spec-file --app-dir . --spec-output-file spec.json
cd ..

cd kilosort2_5
docker build . -t magland/pc-kilosort2_5
docker push magland/pc-kilosort2_5
protocaas make-app-spec-file --app-dir . --spec-output-file spec.json
cd ..

cd kilosort3
docker build . -t magland/pc-kilosort3
docker push magland/pc-kilosort3
protocaas make-app-spec-file --app-dir . --spec-output-file spec.json
cd ..

cd mountainsort5
docker build . -t magland/pc-mountainsort5
docker push magland/pc-mountainsort5
protocaas make-app-spec-file --app-dir . --spec-output-file spec.json
cd ..

cd spike_sorting_utils
docker build . -t magland/pc-spike-sorting-utils
docker push magland/pc-spike-sorting-utils
protocaas make-app-spec-file --app-dir . --spec-output-file spec.json
cd ..