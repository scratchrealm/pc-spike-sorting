#!/bin/bash

set -ex

# dandi_upload
dendro make-app-spec-file --app-dir dandi_upload --spec-output-file dandi_upload/spec.json

# kilosort2_5
dendro make-app-spec-file --app-dir kilosort2_5 --spec-output-file kilosort2_5/spec.json

# kilosort3
dendro make-app-spec-file --app-dir kilosort3 --spec-output-file kilosort3/spec.json

# mountainsort5
dendro make-app-spec-file --app-dir mountainsort5 --spec-output-file mountainsort5/spec.json

# spike_sorting_utils
dendro make-app-spec-file --app-dir spike_sorting_utils --spec-output-file spike_sorting_utils/spec.json

# mountainsort5_dev
dendro make-app-spec-file --app-dir mountainsort5_dev --spec-output-file mountainsort5_dev/spec.json
