#!/usr/bin/env python3

import os
from typing import List
from dataclasses import dataclass
from protocaas.sdk import App, ProcessorBase, field, InputFile, OutputFile


app = App(
    'kilosort2_5',
    help="Kilosort2_5 spike sorting",
    app_image="magland/pc-kilosort2_5",
    app_executable="/app/main.py"
)

description = """
Kilosort 2.5
"""

@dataclass
class Kilsort2_5Context:
    input: InputFile = field(help='input .nwb file')
    output: OutputFile = field(help='output .nwb file')
    electrical_series_path: str = field(help='Path to the electrical series in the NWB file, e.g., /acquisition/ElectricalSeries')
    detect_threshold: float = field(default=6, help="Threshold for spike detection")
    projection_threshold: List[float] = field(default=[10, 4], help="Threshold on projections")
    preclust_threshold: float = field(default=8, help="Threshold crossings for pre-clustering (in PCA projection space)")
    car: bool = field(default=True, help="Enable or disable common reference")
    minFR: float = field(default=0.1, help="Minimum spike rate (Hz), if a cluster falls below this for too long it gets removed")
    minfr_goodchannels: float = field(default=0.1, help="Minimum firing rate on a 'good' channel")
    nblocks: int = field(default=5, help="blocks for registration. 0 turns it off, 1 does rigid registration. Replaces 'datashift' option.")
    sig: float = field(default=20, help="spatial smoothness constant for registration")
    freq_min: float = field(default=150, help="High-pass filter cutoff frequency")
    sigmaMask: float = field(default=30, help="Spatial constant in um for computing residual variance of spike")
    nPCs: int = field(default=3, help="Number of PCA dimensions")
    ntbuff: int = field(default=64, help="Samples of symmetrical buffer for whitening and spike detection")
    nfilt_factor: int = field(default=4, help="Max number of clusters per good channel (even temporary ones) 4")
    NT: int = field(default=-1, help='Batch size (if -1 it is automatically computed)')
    AUCsplit: float = field(default=0.9, help="Threshold on the area under the curve (AUC) criterion for performing a split in the final step")
    do_correction: bool = field(default=True, help="If True drift registration is applied")
    wave_length: float = field(default=61, help="size of the waveform extracted around each detected peak, (Default 61, maximum 81)")
    keep_good_only: bool = field(default=True, help="If True only 'good' units are returned")
    skip_kilosort_preprocessing: bool = field(default=False, help="Can optionaly skip the internal kilosort preprocessing")
    scaleproc: int = field(default=-1, help="int16 scaling of whitened data, if -1 set to 200.")
    test_duration_sec: float = field(default=0, help='For testing purposes: duration of the recording in seconds (0 means all)')

class Kilosort2_5Processor(ProcessorBase):
    name = 'kilosort2_5'
    help = description
    label = 'Kilosort 2.5'
    tags = ['spike_sorting', 'spike_sorter']
    attributes = {'wip': True}
    @staticmethod
    def run(context: Kilsort2_5Context):
        import h5py
        import remfile
        import pynwb
        from NwbRecording import NwbRecording
        from create_sorting_out_nwb_file import create_sorting_out_nwb_file
        from run_kilosort2_5 import run_kilosort2_5
        from make_int16_recording import make_int16_recording
        from print_elapsed_time import print_elapsed_time, start_timer

        print('Starting kilosort2_5 processor')
        start_timer()

        # open the remote file
        print('Opening remote input file')
        remf = remfile.File(input) # input has a get_url() method which will auto-renew the signed download url if it has expired
        f = h5py.File(remf, 'r')
        print_elapsed_time()

        print('Creating input recording')
        recording = NwbRecording(
            file=f,
            electrical_series_path=context.electrical_series_path
        )
        print_elapsed_time()

        if context.test_duration_sec > 0:
            recording = recording.frame_slice(0, int(recording.get_sampling_frequency() * context.test_duration_sec))

        # important to make a binary recording so that it can be serialized in the format expected by kilosort
        # it's important that it's a single segment with int16 dtype
        # during this step, the entire recording will be downloaded to disk
        print('Creating binary recording')
        recording_binary = make_int16_recording(recording, dirname='/tmp/int16_recording')
        print_elapsed_time()

        # run kilosort2_5
        print('Preparing kilosort2_5')
        sorting_params = {
            'detect_threshold': context.detect_threshold,
            'projection_threshold': context.projection_threshold,
            'preclust_threshold': context.preclust_threshold,
            'car': context.car,
            'minFR': context.minFR,
            'minfr_goodchannels': context.minfr_goodchannels,
            'nblocks': context.nblocks,
            'sig': context.sig,
            'freq_min': context.freq_min,
            'sigmaMask': context.sigmaMask,
            'nPCs': context.nPCs,
            'ntbuff': context.ntbuff,
            'nfilt_factor': context.nfilt_factor,
            'do_correction': context.do_correction,
            'NT': context.NT if context.NT >= 0 else None,
            'AUCsplit': context.AUCsplit,
            'wave_length': context.wave_length,
            'keep_good_only': context.keep_good_only,
            'skip_kilosort_preprocessing': context.skip_kilosort_preprocessing,
            'scaleproc': context.scaleproc
        }

        print('Running kilosort2_5')
        os.mkdir('working')
        sorting = run_kilosort2_5(
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
        context.output.set(sorting_out_fname)
        print_elapsed_time()

description_quicktest = """
For running tests. Runs Kilosort 2.5 with default parameters on the first portion of the recording.
"""

@dataclass
class Kilsort2_5QuicktestContext:
    input: InputFile = field(help='input .nwb file')
    output: OutputFile = field(help='output .nwb file')
    electrical_series_path: str = field(help='Path to the electrical series in the NWB file, e.g., /acquisition/ElectricalSeries')
    test_duration_sec: float = field(default=60, help='For testing purposes: duration of the recording in seconds (0 means all)')

class Kilosort2_5QuicktestProcessor(ProcessorBase):
    name = 'ks2_5_quicktest'
    help = description_quicktest
    label = 'Kilosort 2.5 Quick Test'
    tags = ['spike_sorting', 'spike_sorter']
    attributes = {'wip': True}
    @staticmethod
    def run(context: Kilsort2_5QuicktestContext):
        Kilosort2_5Processor.run(
            Kilsort2_5Context(
                input=context.input,
                output=context.output,
                electrical_series_path=context.electrical_series_path,
                detect_threshold=6,
                projection_threshold=[10, 4],
                preclust_threshold=8,
                car=True,
                minFR=0.1,
                minfr_goodchannels=0.1,
                nblocks=5,
                sig=20,
                freq_min=150,
                sigmaMask=30,
                nPCs=3,
                ntbuff=64,
                nfilt_factor=4,
                NT=-1,
                AUCsplit=0.9,
                do_correction=True,
                wave_length=61,
                keep_good_only=True,
                skip_kilosort_preprocessing=False,
                scaleproc=-1,
                test_duration_sec=context.test_duration_sec
            )
        )

app.add_processor(Kilosort2_5Processor)
app.add_processor(Kilosort2_5QuicktestProcessor)

if __name__ == '__main__':
    app.run()
