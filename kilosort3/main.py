#!/usr/bin/env python3

import os
from dendro.sdk import App, ProcessorBase
from models import Kilosort3Context, Kilosort3QuicktestContext

from Kilosort3HamilosLabProcessor import Kilosort3HamilosLabProcessor


app = App(
    'kilosort3',
    description="Kilosort3 spike sorting",
    app_image="ghcr.io/scratchrealm/pc-kilosort3:latest",
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

class Kilosort3Processor(ProcessorBase):
    name = 'kilosort3'
    description = description
    label = 'Kilosort 3'
    tags = ['spike_sorting', 'spike_sorter']
    attributes = {'wip': True}
    @staticmethod
    def run(context: Kilosort3Context):
        import h5py
        import pynwb
        from common.NwbRecording import NwbRecording
        from common.create_sorting_out_nwb_file import create_sorting_out_nwb_file
        from run_kilosort3 import run_kilosort3
        from common.make_int16_recording import make_int16_recording
        from common.print_elapsed_time import print_elapsed_time, start_timer

        print('Starting kilosort3 processor')
        start_timer()

        print('Creating input recording')
        recording = NwbRecording(
            file=context.input.get_file(),
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

        # run kilosort3
        print('Preparing kilosort3')
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
            'scaleproc': context.scaleproc if context.scaleproc >= 0 else None
        }

        print('Running kilosort3')
        sorting = run_kilosort3(
            recording=recording_binary,
            sorting_params=sorting_params,
            output_folder='/tmp/sorting_output'
        )
        print_elapsed_time()

        print('Writing output NWB file')
        h5_file = h5py.File(context.input.get_file(), 'r')
        with pynwb.NWBHDF5IO(file=h5_file, mode='r', load_namespaces=True) as io:
            nwbfile_rec = io.read()

            if not os.path.exists('output'):
                os.mkdir('output')
            sorting_out_fname = 'output/sorting.nwb'

            create_sorting_out_nwb_file(nwbfile_rec=nwbfile_rec, sorting=sorting, sorting_out_fname=sorting_out_fname)
        print_elapsed_time()

        print('Uploading output NWB file')
        context.output.upload(sorting_out_fname)
        print_elapsed_time()

description_quicktest = """
For running tests. Runs Kilosort 3 with default parameters on the first portion of the recording.
"""

class Kilosort3QuicktestProcessor(ProcessorBase):
    name = 'ks3_quicktest'
    description = description_quicktest
    label = 'Kilosort 3 Quick Test'
    tags = ['spike_sorting', 'spike_sorter']
    attributes = {'wip': True}
    @staticmethod
    def run(context: Kilosort3QuicktestContext):
        Kilosort3Processor.run(
            Kilosort3Context(
                input=context.input,
                output=context.output,
                electrical_series_path=context.electrical_series_path,
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
                test_duration_sec=context.test_duration_sec
            )
        )

app.add_processor(Kilosort3Processor)
app.add_processor(Kilosort3QuicktestProcessor)
app.add_processor(Kilosort3HamilosLabProcessor)

if __name__ == '__main__':
    app.run()
