#!/usr/bin/env python3

import os
from dendro.sdk import ProcessorBase, BaseModel, Field, InputFile, OutputFile


class Kilosort3HamilosLabContext(BaseModel):
    input: InputFile = Field(description='input .nwb file')
    output: OutputFile = Field(description='output .nwb file')
    electrical_series_path: str = Field(description='Path to the electrical series in the NWB file, e.g., /acquisition/ElectricalSeries')
    test_duration_sec: float = Field(default=60, description='For testing purposes: duration of the recording in seconds (0 means all)')

class Kilosort3HamilosLabProcessor(ProcessorBase):
    name = 'kilosort3-hamilos-lab'
    description = 'Kilosort3 Hamilos lab processor'
    label = 'Kilosort 3'
    tags = ['spike_sorting', 'spike_sorter']
    attributes = {'wip': True}
    @staticmethod
    def run(context: Kilosort3HamilosLabContext):
        import h5py
        import remfile
        import pynwb
        from NwbRecording import NwbRecording
        from create_sorting_out_nwb_file import create_sorting_out_nwb_file
        from run_kilosort3 import run_kilosort3
        from make_int16_recording import make_int16_recording
        from print_elapsed_time import print_elapsed_time, start_timer

        print('Starting kilosort3 Hamilos lab processor')
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

        # important to make a binary recording so that it can be serialized in the format expected by kilosort
        # it's important that it's a single segment with int16 dtype
        # during this step, the entire recording will be downloaded to disk
        print('Creating binary recording')
        recording_binary = make_int16_recording(recording, dirname='/tmp/int16_recording')
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

            # important to prepare this for kilosort
            recording_group_binary = make_int16_recording(recording_group, dirname=f'/tmp/int16_recording_group_{group}')

            # run kilosort3
            print('Preparing kilosort3')
            sorting_params = {
            }

            print(f'Running kilosort3 on group {group}')
            sorting = run_kilosort3(
                recording=recording_group_binary,
                sorting_params=sorting_params,
                output_folder=f'/tmp/sorting_output_group_{group}'
            )
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
    _numpy_sorting_from_dict([units], sampling_frequency=sorting0.get_sampling_frequency())

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
