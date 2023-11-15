import os
from dendro.sdk import ProcessorBase, BaseModel, Field, InputFile, OutputFile


class Mountainsort5PreprocessingParameters(BaseModel):
    freq_min: int = Field(default=300, description='High-pass filter cutoff frequency')
    freq_max: int = Field(default=6000, description='Low-pass filter cutoff frequency')
    filter: bool = Field(default=True, description='Enable or disable filter')
    whiten: bool = Field(default=True, description='Enable or disable whiten')

class Mountainsort5Scheme2SortingParameters(BaseModel):
    scheme2_phase1_detect_channel_radius: int = Field(default=200, description='Channel radius for excluding events that are too close in time during phase 1 of scheme 2')
    scheme2_detect_channel_radius: int = Field(default=50, description='Channel radius for excluding events that are too close in time during phase 2 of scheme 2')
    scheme2_max_num_snippets_per_training_batch: int = Field(default=200, description='Maximum number of snippets to use in each batch for training during phase 2 of scheme 2')
    scheme2_training_duration_sec: int = Field(default=60 * 5, description='Duration of training data to use in scheme 2')
    scheme2_training_recording_sampling_mode: str = Field(default='uniform', description='initial or uniform', json_schema_extra={'options': ['initial', 'uniform']})


class Mountainsort5HamilosLabContext(BaseModel):
    input: InputFile = Field(description='input .nwb file')
    output: OutputFile = Field(description='output .nwb file')
    electrical_series_path: str = Field(description='Path to the electrical series in the NWB file, e.g., /acquisition/ElectricalSeries')
    scheme: int = Field(default=2, description='Which sorting scheme to use: 1, 2, or 3', json_schema_extra={'options': [1, 2, 3]})
    detect_threshold: float = Field(default=5.5, description='Detection threshold - recommend to use the default')
    detect_sign: int = Field(default=-1, description='Use -1 for detecting negative peaks, 1 for positive, 0 for both', json_schema_extra={'options': [-1, 0, 1]})
    detect_time_radius_msec: float = Field(default=0.5, description='Determines the minimum allowable time interval between detected spikes in the same spatial region')
    snippet_T1: int = Field(default=20, description='Number of samples before the peak to include in the snippet')
    snippet_T2: int = Field(default=20, description='Number of samples after the peak to include in the snippet')
    npca_per_channel: int = Field(default=3, description='Number of PCA features per channel in the initial dimension reduction step')
    npca_per_subdivision: int = Field(default=10, description='Number of PCA features to compute at each stage of clustering in the isosplit6 subdivision method')
    snippet_mask_radius: int = Field(default=250, description='Radius of the mask to apply to the extracted snippets')
    scheme1_detect_channel_radius: int = Field(default=150, description='Channel radius for excluding events that are too close in time in scheme 1')
    scheme2: Mountainsort5Scheme2SortingParameters = Field(description='Parameters for scheme 2') # indicate somehow that this is active only if scheme == 2 or 3
    scheme3_block_duration_sec: int = Field(default=60 * 30, description='Duration of each block in scheme 3') # indicate somehow that this is active only if scheme == 3
    preprocessing: Mountainsort5PreprocessingParameters = Field(description='Preprocessing parameters')
    test_duration_sec: float = Field(default=0, description='For testing purposes: duration of the recording in seconds (0 means all)')

class Mountainsort5HamilosLabProcessor(ProcessorBase):
    name = 'mountainsort5-hamilos-lab'
    description = 'Mountainsort5 Hamilos lab processor'
    label = 'MountainSort 5 Hamilos lab'
    tags = ['spike_sorting', 'spike_sorter']
    attributes = {'wip': True}
    @staticmethod
    def run(context: Mountainsort5HamilosLabContext):
        import h5py
        import remfile
        import pynwb
        import mountainsort5 as ms5
        import spikeinterface as si
        import spikeinterface.preprocessing as spre
        from NwbRecording import NwbRecording
        from make_float32_recording import make_float32_recording
        from _scale_recording_if_float_type import _scale_recording_if_float_type
        from create_sorting_out_nwb_file import create_sorting_out_nwb_file
        from print_elapsed_time import print_elapsed_time, start_timer

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
            recording_filtered = spre.bandpass_filter(recording, freq_min=context.preprocessing.freq_min, freq_max=context.preprocessing.freq_max)
        else:
            print('Filtering off')
            recording_filtered = recording

        print('Creating binary recording')
        recording_binary = make_float32_recording(recording_filtered, dirname='/tmp/int16_recording')
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
