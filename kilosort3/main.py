#!/usr/bin/env python3

import os
from typing import List
import protocaas.sdk as pr


app = pr.App(
    'kilosort3', 
    help="Kilosort3 spike sorting",
    app_image="magland/pc-kilosort3",
    app_executable="/app/main.py"
)

description = """
Kilosort3 is a spike sorting software package developed by Marius Pachitariu at Janelia Research Campus.
It uses a GPU-accelerated algorithm to detect, align, and cluster spikes across many channels.
Building on previous versions, Kilosort3 offers improved efficiency and accuracy in the extraction of neural spike waveforms from multichannel electrophysiological recordings.
By leveraging parallel processing capabilities of modern GPUs, it enables sorting with minimal manual intervention.
This tool has become an essential part of the workflow many electrophysiology labs.
For more information see https://github.com/MouseLand/Kilosort
"""

@pr.processor('kilosort3', help=description)
@pr.attribute('wip', True)
@pr.attribute('label', 'Kilosort 3')
@pr.tags(['spike_sorting', 'spike_sorter'])
@pr.input('input', help='input .nwb file')
@pr.output('output', help='output .nwb file')
@pr.parameter('electrical_series_path', type=str, help='Path to the electrical series in the NWB file, e.g., /acquisition/ElectricalSeries')
@pr.parameter('detect_threshold', type=float, default=6, help='Threshold for spike detection')
@pr.parameter('projection_threshold', type=List[float], default=[9, 9], help='Threshold on projections')
@pr.parameter('preclust_threshold', type=float, default=8, help='Threshold crossings for pre-clustering (in PCA projection space)')
@pr.parameter('car', type=bool, default=True, help='Enable or disable common reference')
@pr.parameter('minFR', type=float, default=0.2, help='Minimum spike rate (Hz), if a cluster falls below this for too long it gets removed')
@pr.parameter('minfr_goodchannels', type=float, default=0.2, help='Minimum firing rate on a "good" channel')
@pr.parameter('nblocks', type=int, default=5, help='blocks for registration. 0 turns it off, 1 does rigid registration. Replaces "datashift" option.')
@pr.parameter('sig', type=float, default=20, help='spatial smoothness constant for registration')
@pr.parameter('freq_min', type=float, default=300, help='High-pass filter cutoff frequency')
@pr.parameter('sigmaMask', type=float, default=30, help='Spatial constant in um for computing residual variance of spike')
@pr.parameter('nPCs', type=int, default=3, help='Number of PCA dimensions')
@pr.parameter('ntbuff', type=int, default=64, help='Samples of symmetrical buffer for whitening and spike detection')
@pr.parameter('nfilt_factor', type=int, default=4, help='Max number of clusters per good channel (even temporary ones) 4')
@pr.parameter('do_correction', type=bool, default=True, help='If True drift registration is applied')
@pr.parameter('NT', type=int, default=-1, help='Batch size (if -1 it is automatically computed)')
@pr.parameter('AUCsplit', type=float, default=0.8, help='Threshold on the area under the curve (AUC) criterion for performing a split in the final step')
@pr.parameter('wave_length', type=int, default=61, help='size of the waveform extracted around each detected peak, (Default 61, maximum 81)')
@pr.parameter('keep_good_only', type=bool, default=True, help='If True only "good" units are returned')
@pr.parameter('skip_kilosort_preprocessing', type=bool, default=False, help='Can optionaly skip the internal kilosort preprocessing')
@pr.parameter('scaleproc', type=int, default=-1, help='int16 scaling of whitened data, if -1 set to 200.')
@pr.parameter('test_duration_sec', type=float, default=0, help='For testing purposes: duration of the recording in seconds (0 means all)')
def kilosort3(
    input: pr.InputFile,
    output: pr.OutputFile,
    electrical_series_path: str,
    detect_threshold: float,
    projection_threshold: List[float],
    preclust_threshold: float,
    car: bool,
    minFR: float,
    minfr_goodchannels: float,
    nblocks: int,
    sig: int,
    freq_min: int,
    sigmaMask: int,
    nPCs: int,
    ntbuff: int,
    nfilt_factor: int,
    do_correction: bool,
    NT: int,
    AUCsplit: float,
    wave_length: int,
    keep_good_only: bool,
    skip_kilosort_preprocessing: bool,
    scaleproc: int,
    test_duration_sec: float
):
    import h5py
    import remfile
    import pynwb
    from NwbRecording import NwbRecording
    from create_sorting_out_nwb_file import create_sorting_out_nwb_file 
    from run_kilosort3 import run_kilosort3
    from make_int16_recording import make_int16_recording
    from print_elapsed_time import print_elapsed_time, start_timer
    
    print('Starting kilosort3 processor')
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

    # important to make a binary recording so that it can be serialized in the format expected by kilosort
    # it's important that it's a single segment with int16 dtype
    # during this step, the entire recording will be downloaded to disk
    print('Creating binary recording')
    recording_binary = make_int16_recording(recording, dirname='/tmp/int16_recording')
    print_elapsed_time()

    # run kilosort3
    print('Preparing kilosort3')
    sorting_params = {
        'detect_threshold': detect_threshold,
        'projection_threshold': projection_threshold,
        'preclust_threshold': preclust_threshold,
        'car': car,
        'minFR': minFR,
        'minfr_goodchannels': minfr_goodchannels,
        'nblocks': nblocks,
        'sig': sig,
        'freq_min': freq_min,
        'sigmaMask': sigmaMask,
        'nPCs': nPCs,
        'ntbuff': ntbuff,
        'nfilt_factor': nfilt_factor,
        'do_correction': do_correction,
        'NT': NT if NT >= 0 else None,
        'AUCsplit': AUCsplit,
        'wave_length': wave_length,
        'keep_good_only': keep_good_only,
        'skip_kilosort_preprocessing': skip_kilosort_preprocessing,
        'scaleproc': scaleproc if scaleproc >= 0 else None
    }

    print('Running kilosort3')
    os.mkdir('working')
    sorting = run_kilosort3(
        recording=recording_binary,
        sorting_params=sorting_params
    )
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
For running tests. Runs Kilosort 3 with default parameters on the first portion of the recording.
"""

@pr.processor('ks3_quicktest', help=description_quicktest)
@pr.attribute('wip', True)
@pr.attribute('label', 'Kilosort 3 Quick Test')
@pr.tags(['spike_sorting', 'spike_sorter'])
@pr.input('input', help='input .nwb file')
@pr.output('output', help='output .nwb file')
@pr.parameter('electrical_series_path', type=str, help='Path to the electrical series in the NWB file, e.g., /acquisition/ElectricalSeries')
@pr.parameter('test_duration_sec', type=float, default=60, help='For testing purposes: duration of the recording in seconds (0 means all)')
def ks3_quicktest(
    input: pr.InputFile,
    output: pr.OutputFile,
    electrical_series_path: str,
    test_duration_sec: float
):
    kilosort3(
        input=input,
        output=output,
        electrical_series_path=electrical_series_path,
        detect_threshold=6,
        projection_threshold=[9, 9],
        preclust_threshold=8,
        car=True,
        minFR=0.2,
        minfr_goodchannels=0.2,
        nblocks=5,
        sig=20,
        freq_min=300,
        sigmaMask=30,
        nPCs=3,
        ntbuff=64,
        nfilt_factor=4,
        do_correction=True,
        NT=-1,
        AUCsplit=0.8,
        wave_length=61,
        keep_good_only=True,
        skip_kilosort_preprocessing=False,
        scaleproc=-1,
        test_duration_sec=test_duration_sec
    )

app.add_processor(kilosort3)
app.add_processor(ks3_quicktest)

if __name__ == '__main__':
    app.run()