#!/bin/bash

set -ex

# dandi_upload
dendro make-app-spec-file --app-dir dandi_upload --spec-output-file dandi_upload/spec.json
docker build -f dandi_upload/Dockerfile . -t magland/pc-dandi-upload
docker push magland/pc-dandi-upload

# kilosort2_5
dendro make-app-spec-file --app-dir kilosort2_5 --spec-output-file kilosort2_5/spec.json
docker build -f kilosort2_5/Dockerfile . -t magland/pc-kilosort2_5
docker push magland/pc-kilosort2_5

# kilosort3
dendro make-app-spec-file --app-dir kilosort3 --spec-output-file kilosort3/spec.json
docker build -f kilosort3/Dockerfile . -t magland/pc-kilosort3
docker push magland/pc-kilosort3

# mountainsort5
dendro make-app-spec-file --app-dir mountainsort5 --spec-output-file mountainsort5/spec.json
docker build -f mountainsort5/Dockerfile . -t magland/pc-mountainsort5
docker push magland/pc-mountainsort5

# spike_sorting_utils
dendro make-app-spec-file --app-dir spike_sorting_utils --spec-output-file spike_sorting_utils/spec.json
docker build -f spike_sorting_utils/Dockerfile . -t magland/pc-spike-sorting-utils
docker push magland/pc-spike-sorting-utils
