import os
import shutil
from pathlib import Path
import subprocess
import numpy as np
import spikeinterface as si
import spikeinterface.sorters as ss
import spikeinterface.extractors as se

def run_kilosort3(
    *,
    recording: si.BinaryRecordingExtractor,
    output_folder: str,
    sorting_params: dict={}
) -> si.BaseSorting:
    print('')
    print('Binary recording info:')
    print(f'Sampling frequency (Hz): {recording.get_sampling_frequency()}')
    print(f'Num. channels: {recording.get_num_channels()}')
    print(f'Duration (s): {recording.get_num_frames() / recording.get_sampling_frequency()}')
    print(f'Num. frames: {recording.get_num_frames()}')
    print(f'Dtype: {recording.get_dtype()}')
    print('')

    # check recording
    print('Checking recording')
    if recording.get_num_segments() > 1:
        raise NotImplementedError("Multi-segment recordings are not supported yet")
    if recording.dtype != "int16":
        raise ValueError("Recording dtype must be int16")
    
    binary_file_path = recording._kwargs["file_paths"][0]
    print(f'Using binary file path: {binary_file_path}')
    binary_file_path = Path(binary_file_path)

    sorting = ss.run_sorter('kilosort3', **sorting_params)

    return sorting