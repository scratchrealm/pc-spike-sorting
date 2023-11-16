import os
import numpy as np
from dendro.sdk import ProcessorBase
from models import Mountainsort5ProcessorContext

class Mountainsort5HamilosLabProcessor(ProcessorBase):
    name = 'mountainsort5-hamiloslab'
    description = 'Mountainsort5 Hamilos Lab processor'
    label = 'MountainSort 5 Hamilos Lab'
    tags = ['spike_sorting', 'spike_sorter']
    attributes = {'wip': True}
    @staticmethod
    def run(context: Mountainsort5ProcessorContext):
        import h5py
        import remfile
        import pynwb
        import mountainsort5 as ms5
        import spikeinterface as si
        import spikeinterface.preprocessing as spre
        from common.NwbRecording import NwbRecording
        from common.make_float32_recording import make_float32_recording
        from common._scale_recording_if_float_type import _scale_recording_if_float_type
        from common.create_sorting_out_nwb_file import create_sorting_out_nwb_file
        from common.print_elapsed_time import print_elapsed_time, start_timer

        print('Starting MountainSort5 Hamilos lab processor')
        start_timer()

        # open the remote file
        print('Opening remote input file')
        remf = remfile.File(context.input) # input has a get_url() method which will auto-renew the signed download url if it has expired
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

        # bandpass filter
        if context.preprocessing.filter:
            print('Filtering on')
            recording_filtered = spre.bandpass_filter(recording, freq_min=context.preprocessing.freq_min, freq_max=context.preprocessing.freq_max, dtype=np.float32) # important to specify dtype here
        else:
            print('Filtering off')
            recording_filtered = recording

        print('Creating binary recording')
        recording_binary = make_float32_recording(recording_filtered, dirname='/tmp/float32_recording')
        print_elapsed_time()

        channel_groups = recording.get_channel_groups() # get this from recording, not recording_binary
        unique_channel_groups = sorted(list(set(channel_groups)))
        print(f'Channel groups: {unique_channel_groups}')

        sortings = []
        for group in unique_channel_groups:
            print(f'Processing group {group}')
            channel_ids_in_group = [ch for ch in recording.get_channel_ids() if recording.get_channel_property(ch, 'group') == group] # get this from recording, not recording_binary
            print(f'Channels: {channel_ids_in_group}')
            recording_group = recording_binary.channel_slice(channel_ids=channel_ids_in_group)

            # whiten
            if context.preprocessing.whiten:
                print('Whitening on')
                # see comment below in _scale_recording_if_float_type
                recording_scaled = _scale_recording_if_float_type(recording_group)
                recording_group_preprocessed: si.BaseRecording = spre.whiten(
                    recording_scaled,
                    dtype='float32',
                    num_chunks_per_segment=1, # by default this is 20 which takes a long time to load depending on the chunking
                    chunk_size=int(1e5)
                )
            else:
                print('Whitening off')
                recording_group_preprocessed = recording_group

            recording_group_preprocessed = make_float32_recording(recording_group_preprocessed, dirname=f'/tmp/preprocessed_recording_group_{group}')

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
                sorting = ms5.sorting_scheme1(recording=recording_group_preprocessed, sorting_parameters=scheme1_sorting_parameters)
            elif context.scheme == 2:
                print('Sorting scheme 2')
                sorting = ms5.sorting_scheme2(recording=recording_group_preprocessed, sorting_parameters=scheme2_sorting_parameters)
            elif context.scheme == 3:
                print('Sorting scheme 3')
                sorting = ms5.sorting_scheme3(recording=recording_group_preprocessed, sorting_parameters=scheme3_sorting_parameters)
            else:
                raise ValueError(f'Unexpected scheme: {context.scheme}')
            print_elapsed_time()

            sortings.append(sorting)

        print('Combining sortings')
        sorting = _combine_sortings(sortings, group_ids=unique_channel_groups)
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

def _combine_sortings(sortings, group_ids):
    from typing import Dict
    import numpy as np
    import spikeinterface as si
    sorting0: si.BaseSorting = sortings[0]
    units: Dict[str, np.ndarray] = {}
    for ii, sorting in enumerate(sortings):
        for unit_id in sorting.get_unit_ids():
            if unit_id not in units:
                uid = f'{group_ids[ii]}-{unit_id}'
                units[uid] = sorting.get_unit_spike_train(unit_id)
    return _numpy_sorting_from_dict([units], sampling_frequency=sorting0.get_sampling_frequency())

def _numpy_sorting_from_dict(units_dict_list, *, sampling_frequency):
    import spikeinterface as si
    try:
        # different versions of spikeinterface
        # see: https://github.com/SpikeInterface/spikeinterface/issues/2083
        sorting = si.NumpySorting.from_dict( # type: ignore
            units_dict_list, sampling_frequency=sampling_frequency
        )
    except: # noqa
        sorting = si.NumpySorting.from_unit_dict( # type: ignore
            units_dict_list, sampling_frequency=sampling_frequency
        )
    return sorting
