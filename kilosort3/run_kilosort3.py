import os
from pathlib import Path
import spikeinterface as si
import spikeinterface.sorters as ss

def run_kilosort3(
    *,
    recording: si.BinaryRecordingExtractor,
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
    if recording.get_dtype().kind != 'i':
        raise ValueError("Recording dtype must be int16")
    
    binary_file_path = recording._kwargs["file_paths"][0]
    print(f'Using binary file path: {binary_file_path}')
    binary_file_path = Path(binary_file_path)

    os.environ['HOME'] = '/tmp' # we set /tmp to be the home dir because ks3_compiled prepares matlab runtime stuff in the home dir, and that may not exist if this whole thing is running in singularity using the --contain flag
    sorting = ss.run_sorter('kilosort3', recording, **sorting_params, verbose=True)
    if not sorting:
        raise Exception('Sorting failed')

    return sorting # type: ignore