#!/usr/bin/env python3

import os
from dendro.sdk import App, ProcessorBase
from Mountainsort5HamilosLabProcessor import Mountainsort5HamilosLabProcessor
from models import Mountainsort5PreprocessingParameters, Mountainsort5Scheme2SortingParameters, Mountainsort5ProcessorContext, MS5QuickTestProcessorContext


app = App(
    'mountainsort5',
    description="MountainSort5 spike sorting",
    app_image="magland/pc-mountainsort5",
    app_executable="/app/main.py"
)

description = """
MountainSort is a CPU-based spike sorting software package developed by Jeremy Magland and others at Flatiron Institute in collaboration with researchers at Loren Frank's lab.
By employing Isosplit, a non-parametric density-based clustering approach, the software minimizes the need for manual intervention, thereby reducing errors and inconsistencies.
See https://github.com/flatironinstitute/mountainsort5 and https://doi.org/10.1016/j.neuron.2017.08.030
"""

class Mountainsort5Processor(ProcessorBase):
    name = 'mountainsort5'
    label = 'MountainSort 5 spike sorter'
    description = description
    tags = ['spike_sorting', 'spike_sorter']
    attributes = {
        'wip': True
    }

    @staticmethod
    def run(context: Mountainsort5ProcessorContext):
        import h5py
        import spikeinterface as si
        import pynwb
        from common.NwbRecording import NwbRecording
        from common.create_sorting_out_nwb_file import create_sorting_out_nwb_file
        import spikeinterface.preprocessing as spre
        import mountainsort5 as ms5
        from common.make_float32_recording import make_float32_recording
        from common.print_elapsed_time import print_elapsed_time, start_timer
        from common._scale_recording_if_float_type import _scale_recording_if_float_type

        input = context.input
        output = context.output

        print('Starting mountainsort5 processor')
        start_timer()

        # open the remote file
        print('Opening remote input file')
        f = h5py.File(context.input.get_file(), 'r')
        print_elapsed_time()

        print('Creating input recording')
        recording = NwbRecording(
            file=f,
            electrical_series_path=context.electrical_series_path
        )
        print_elapsed_time()

        if context.test_duration_sec > 0:
            recording = recording.frame_slice(0, int(recording.get_sampling_frequency() * context.test_duration_sec))

        # Make sure the recording is preprocessed appropriately
        # lazy preprocessing
        if context.preprocessing.filter:
            print('Filtering on')
            recording_filtered = spre.bandpass_filter(recording, freq_min=context.preprocessing.freq_min, freq_max=context.preprocessing.freq_max)
        else:
            print('Filtering off')
            recording_filtered = recording
        if context.preprocessing.whiten:
            print('Whitening on')
            # see comment below in _scale_recording_if_float_type
            recording_scaled = _scale_recording_if_float_type(recording_filtered)
            recording_preprocessed: si.BaseRecording = spre.whiten(
                recording_scaled,
                dtype='float32',
                num_chunks_per_segment=1, # by default this is 20 which takes a long time to load depending on the chunking
                chunk_size=int(1e5)
            )
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
            detect_threshold=context.detect_threshold,
            detect_channel_radius=context.scheme1_detect_channel_radius,
            detect_time_radius_msec=context.detect_time_radius_msec,
            detect_sign=context.detect_sign,
            snippet_T1=context.snippet_T1,
            snippet_T2=context.snippet_T2,
            snippet_mask_radius=context.snippet_mask_radius,
            npca_per_channel=context.npca_per_channel,
            npca_per_subdivision=context.npca_per_subdivision
        )

        scheme2_sorting_parameters = ms5.Scheme2SortingParameters(
            phase1_detect_channel_radius=context.scheme2.scheme2_phase1_detect_channel_radius,
            detect_channel_radius=context.scheme2.scheme2_detect_channel_radius,
            phase1_detect_threshold=context.detect_threshold,
            phase1_detect_time_radius_msec=context.detect_time_radius_msec,
            detect_time_radius_msec=context.detect_time_radius_msec,
            phase1_npca_per_channel=context.npca_per_channel,
            phase1_npca_per_subdivision=context.npca_per_subdivision,
            detect_sign=context.detect_sign,
            detect_threshold=context.detect_threshold,
            snippet_T1=context.snippet_T1,
            snippet_T2=context.snippet_T2,
            snippet_mask_radius=context.snippet_mask_radius,
            max_num_snippets_per_training_batch=context.scheme2.scheme2_max_num_snippets_per_training_batch,
            classifier_npca=None,
            training_duration_sec=context.scheme2.scheme2_training_duration_sec,
            training_recording_sampling_mode=context.scheme2.scheme2_training_recording_sampling_mode # type: ignore
        )

        scheme3_sorting_parameters = ms5.Scheme3SortingParameters(
            block_sorting_parameters=scheme2_sorting_parameters, block_duration_sec=context.scheme3_block_duration_sec
        )

        if context.scheme == 1:
            print('Sorting scheme 1')
            sorting = ms5.sorting_scheme1(recording=recording_binary, sorting_parameters=scheme1_sorting_parameters)
        elif context.scheme == 2:
            print('Sorting scheme 2')
            sorting = ms5.sorting_scheme2(recording=recording_binary, sorting_parameters=scheme2_sorting_parameters)
        elif context.scheme == 3:
            print('Sorting scheme 3')
            sorting = ms5.sorting_scheme3(recording=recording_binary, sorting_parameters=scheme3_sorting_parameters)
        else:
            raise ValueError(f'Unexpected scheme: {context.scheme}')
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

class MS5QuickTestProcessor(ProcessorBase):
    name = 'ms5_quicktest'
    label = 'MountainSort5 Quick Test'
    description = description_quicktest
    tags = ['spike_sorting', 'spike_sorter']
    attributes = {
        'wip': True
    }

    @staticmethod
    def run(context: MS5QuickTestProcessorContext):
        input = context.input
        output = context.output
        electrical_series_path = context.electrical_series_path
        test_duration_sec = context.test_duration_sec

        context0 = Mountainsort5ProcessorContext(
            input=input,
            output=output,
            electrical_series_path=electrical_series_path,
            scheme=1,
            detect_threshold=5.5,
            detect_sign=-1,
            detect_time_radius_msec=0.5,
            snippet_T1=20,
            snippet_T2=20,
            npca_per_channel=3,
            npca_per_subdivision=10,
            snippet_mask_radius=250,
            scheme1_detect_channel_radius=150,
            scheme2=Mountainsort5Scheme2SortingParameters(
                scheme2_phase1_detect_channel_radius=200,
                scheme2_detect_channel_radius=50,
                scheme2_max_num_snippets_per_training_batch=200,
                scheme2_training_duration_sec=60 * 5,
                scheme2_training_recording_sampling_mode='uniform'
            ),
            scheme3_block_duration_sec=60 * 30,
            preprocessing=Mountainsort5PreprocessingParameters(
                freq_min=300,
                freq_max=6000,
                filter=True,
                whiten=True
            ),
            test_duration_sec=test_duration_sec
        )

        Mountainsort5Processor.run(context0)

app.add_processor(Mountainsort5Processor)
app.add_processor(MS5QuickTestProcessor)
app.add_processor(Mountainsort5HamilosLabProcessor)

if __name__ == '__main__':
    app.run()
