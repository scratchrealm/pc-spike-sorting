#!/usr/bin/env python3

import os
import numpy as np
import protocaas.sdk as pr


app = pr.App(
    'mountainsort5', 
    help="MountainSort5 spike sorting",
    app_image="magland/pc-mountainsort5",
    app_executable="/app/main.py"
)

description = """
MountainSort is a CPU-based spike sorting software package developed by Jeremy Magland and others at Flatiron Institute in collaboration with researchers at Loren Frank's lab.
By employing Isosplit, a non-parametric density-based clustering approach, the software minimizes the need for manual intervention, thereby reducing errors and inconsistencies.
See https://github.com/flatironinstitute/mountainsort5 and https://doi.org/10.1016/j.neuron.2017.08.030
"""

@pr.processor('mountainsort5', help=description)
@pr.attribute('wip', True)
@pr.attribute('label', 'MountainSort 5')
@pr.tags(['spike_sorting', 'spike_sorter'])
@pr.input('input', help='input .nwb file')
@pr.output('output', help='output .nwb file')
@pr.parameter('electrical_series_path', type=str, help='Path to the electrical series in the NWB file, e.g., /acquisition/ElectricalSeries')
@pr.parameter('scheme', type=int, default=2, help='Which sorting scheme to use: 1, 2, or 3', options=[1, 2, 3])
@pr.parameter('detect_threshold', type=float, default=5.5, help='Detection threshold - recommend to use the default')
@pr.parameter('detect_sign', type=int, default=-1, help='Use -1 for detecting negative peaks, 1 for positive, 0 for both', options=[-1, 0, 1])
@pr.parameter('detect_time_radius_msec', type=float, default=0.5, help='Determines the minimum allowable time interval between detected spikes in the same spatial region')
@pr.parameter('snippet_T1', type=int, default=20, help='Number of samples before the peak to include in the snippet')
@pr.parameter('snippet_T2', type=int, default=20, help='Number of samples after the peak to include in the snippet')
@pr.parameter('npca_per_channel', type=int, default=3, help='Number of PCA features per channel in the initial dimension reduction step')
@pr.parameter('npca_per_subdivision', type=int, default=10, help='Number of PCA features to compute at each stage of clustering in the isosplit6 subdivision method')
@pr.parameter('snippet_mask_radius', type=float, default=250, help='Radius of the mask to apply to the extracted snippets')
@pr.parameter('scheme1_detect_channel_radius', type=float, default=150, help='Channel radius for excluding events that are too close in time in scheme 1')
@pr.parameter('scheme2_phase1_detect_channel_radius', type=float, default=200, help='Channel radius for excluding events that are too close in time during phase 1 of scheme 2')
@pr.parameter('scheme2_detect_channel_radius', type=float, default=50, help='Channel radius for excluding events that are too close in time during phase 2 of scheme 2')
@pr.parameter('scheme2_max_num_snippets_per_training_batch', type=int, default=200, help='Maximum number of snippets to use in each batch for training during phase 2 of scheme 2')
@pr.parameter('scheme2_training_duration_sec', type=float, default=60 * 5, help='Duration of training data to use in scheme 2')
@pr.parameter('scheme2_training_recording_sampling_mode', type=str, default='uniform', help='initial or uniform', options=['initial', 'uniform'])
@pr.parameter('scheme3_block_duration_sec', type=float, default=60 * 30, help='Duration of each block in scheme 3')
@pr.parameter('freq_min', type=float, default=300, help='High-pass filter cutoff frequency')
@pr.parameter('freq_max', type=float, default=6000, help='Low-pass filter cutoff frequency')
@pr.parameter('filter', type=bool, default=True, help='Enable or disable filter')
@pr.parameter('whiten', type=bool, default=True, help='Enable or disable whiten')
@pr.parameter('test_duration_sec', type=float, default=0, help='For testing purposes: duration of the recording in seconds (0 means all)')
def mountainsort5(
    input: pr.InputFile,
    output: pr.OutputFile,
    electrical_series_path: str,
    scheme: int,
    detect_threshold: float,
    detect_sign: int,
    detect_time_radius_msec: float,
    snippet_T1: int,
    snippet_T2: int,
    npca_per_channel: int,
    npca_per_subdivision: int,
    snippet_mask_radius: int,
    scheme1_detect_channel_radius: int,
    scheme2_phase1_detect_channel_radius: int,
    scheme2_detect_channel_radius: int,
    scheme2_max_num_snippets_per_training_batch: int,
    scheme2_training_duration_sec: int,
    scheme2_training_recording_sampling_mode: str,
    scheme3_block_duration_sec: int,
    freq_min: int,
    freq_max: int,
    filter: bool,
    whiten: bool,
    test_duration_sec: float
):
    import h5py
    import spikeinterface as si
    import remfile
    import pynwb
    from NwbRecording import NwbRecording
    from create_sorting_out_nwb_file import create_sorting_out_nwb_file 
    import spikeinterface.preprocessing as spre
    import mountainsort5 as ms5
    from make_float32_recording import make_float32_recording
    from print_elapsed_time import print_elapsed_time, start_timer
    from _scale_recording_if_float_type import _scale_recording_if_float_type

    print('Starting mountainsort5 processor')
    start_timer()

    # open the remote file
    print('Opening remote input file')
    remf = remfile.File(input) # input has a get_url() method which will auto-renew the signed download url if it has expired
    f = h5py.File(remf, 'r')
    print_elapsed_time()

    print('Creating input recording')
    recording = NwbRecording(
        file=f,
        electrical_series_path=electrical_series_path
    )
    print_elapsed_time()

    if test_duration_sec > 0:
        recording = recording.frame_slice(0, int(recording.get_sampling_frequency() * test_duration_sec))

    # Make sure the recording is preprocessed appropriately
    # lazy preprocessing
    if filter:
        print('Filtering on')
        recording_filtered = spre.bandpass_filter(recording, freq_min=freq_min, freq_max=freq_max)
    else:
        print('Filtering off')
        recording_filtered = recording
    if whiten:
        print('Whitening on')
        # see comment below in _scale_recording_if_float_type
        recording_scaled = _scale_recording_if_float_type(recording_filtered)
        recording_preprocessed: si.BaseRecording = spre.whiten(recording_scaled, dtype='float32')
    else:
        print('Whitening off')
        recording_preprocessed = recording_filtered
    print_elapsed_time()
    
    # Maybe sometime in the future we will spike sort while lazy loading
    # but for now we're going to download the entire recording to disk first.
    # Probably lazy loading in a smart way would be in order for scheme 3
    # at some point in the future.
    print('Creating binary recording')
    recording_binary = make_float32_recording(recording_preprocessed, dirname='/tmp/preprocessed_recording')
    print_elapsed_time()

    print('Setting up sorting parameters')
    scheme1_sorting_parameters = ms5.Scheme1SortingParameters(
        detect_threshold=detect_threshold,
        detect_channel_radius=scheme1_detect_channel_radius,
        detect_time_radius_msec=detect_time_radius_msec,
        detect_sign=detect_sign,
        snippet_T1=snippet_T1,
        snippet_T2=snippet_T2,
        snippet_mask_radius=snippet_mask_radius,
        npca_per_channel=npca_per_channel,
        npca_per_subdivision=npca_per_subdivision
    )

    scheme2_sorting_parameters = ms5.Scheme2SortingParameters(
        phase1_detect_channel_radius=scheme2_phase1_detect_channel_radius,
        detect_channel_radius=scheme2_detect_channel_radius,
        phase1_detect_threshold=detect_threshold,
        phase1_detect_time_radius_msec=detect_time_radius_msec,
        detect_time_radius_msec=detect_time_radius_msec,
        phase1_npca_per_channel=npca_per_channel,
        phase1_npca_per_subdivision=npca_per_subdivision,
        detect_sign=detect_sign,
        detect_threshold=detect_threshold,
        snippet_T1=snippet_T1,
        snippet_T2=snippet_T2,
        snippet_mask_radius=snippet_mask_radius,
        max_num_snippets_per_training_batch=scheme2_max_num_snippets_per_training_batch,
        classifier_npca=None,
        training_duration_sec=scheme2_training_duration_sec,
        training_recording_sampling_mode=scheme2_training_recording_sampling_mode # type: ignore
    )

    scheme3_sorting_parameters = ms5.Scheme3SortingParameters(
        block_sorting_parameters=scheme2_sorting_parameters, block_duration_sec=scheme3_block_duration_sec
    )

    if scheme == 1:
        print('Sorting scheme 1')
        sorting = ms5.sorting_scheme1(recording=recording_binary, sorting_parameters=scheme1_sorting_parameters)
    elif scheme == 2:
        print('Sorting scheme 2')
        sorting = ms5.sorting_scheme2(recording=recording_binary, sorting_parameters=scheme2_sorting_parameters)
    elif scheme == 3:
        print('Sorting scheme 3')
        sorting = ms5.sorting_scheme3(recording=recording_binary, sorting_parameters=scheme3_sorting_parameters)
    else:
        raise Exception(f'Unexpected scheme: {scheme}')
    print_elapsed_time()

    print('Writing output NWB file')
    with pynwb.NWBHDF5IO(file=f, mode='r', load_namespaces=True) as io:
        nwbfile_rec = io.read()
        
        if not os.path.exists('output'):
            os.mkdir('output')
        sorting_out_fname = 'output/sorting.nwb'

        create_sorting_out_nwb_file(nwbfile_rec=nwbfile_rec, sorting=sorting, sorting_out_fname=sorting_out_fname)
    print_elapsed_time()
    
    print('Uploading output NWB file')
    output.set(sorting_out_fname)
    print_elapsed_time()



description_quicktest = """
For running tests. Runs MountainSort5 scheme 1 with default parameters on the first portion of the recording.
"""

@pr.processor('ms5_quicktest', help=description_quicktest)
@pr.attribute('wip', True)
@pr.attribute('label', 'MountainSort5 Quick Test')
@pr.tags(['spike_sorting', 'spike_sorter'])
@pr.input('input', help='input .nwb file')
@pr.output('output', help='output .nwb file')
@pr.parameter('electrical_series_path', type=str, help='Path to the electrical series in the NWB file, e.g., /acquisition/ElectricalSeries')
@pr.parameter('test_duration_sec', type=float, default=60, help='For testing purposes: duration of the recording in seconds (0 means all)')
def ms5_quicktest(
    input: pr.InputFile,
    output: pr.OutputFile,
    electrical_series_path: str,
    test_duration_sec: float
):
    mountainsort5(
        input=input,
        output=output,
        electrical_series_path=electrical_series_path,
        scheme=2,
        detect_threshold=5.5,
        detect_sign=-1,
        detect_time_radius_msec=0.5,
        snippet_T1=20,
        snippet_T2=20,
        npca_per_channel=3,
        npca_per_subdivision=10,
        snippet_mask_radius=250,
        scheme1_detect_channel_radius=150,
        scheme2_phase1_detect_channel_radius=200,
        scheme2_detect_channel_radius=50,
        scheme2_max_num_snippets_per_training_batch=200,
        scheme2_training_duration_sec=60 * 5,
        scheme2_training_recording_sampling_mode='uniform',
        scheme3_block_duration_sec=60 * 30,
        freq_min=300,
        freq_max=6000,
        filter=True,
        whiten=True,
        test_duration_sec=test_duration_sec
    )

app.add_processor(mountainsort5)
app.add_processor(ms5_quicktest)

if __name__ == '__main__':
    app.run()