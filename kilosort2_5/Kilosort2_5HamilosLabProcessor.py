from typing import List
import os
from dendro.sdk import ProcessorBase, BaseModel, Field, InputFile, OutputFile


class Kilosort2_5HamilosLabContext(BaseModel):
    input: InputFile = Field(description='input .nwb file')
    output: OutputFile = Field(description='output .nwb file')
    electrical_series_path: str = Field(description='Path to the electrical series in the NWB file, e.g., /acquisition/ElectricalSeries')
    detect_threshold: float = Field(default=6, description="Threshold for spike detection")
    projection_threshold: List[float] = Field(default=[10, 4], description="Threshold on projections")
    preclust_threshold: float = Field(default=8, description="Threshold crossings for pre-clustering (in PCA projection space)")
    car: bool = Field(default=True, description="Enable or disable common reference")
    minFR: float = Field(default=0.1, description="Minimum spike rate (Hz), if a cluster falls below this for too long it gets removed")
    minfr_goodchannels: float = Field(default=0.1, description="Minimum firing rate on a 'good' channel")
    nblocks: int = Field(default=5, description="blocks for registration. 0 turns it off, 1 does rigid registration. Replaces 'datashift' option.")
    sig: float = Field(default=20, description="spatial smoothness constant for registration")
    freq_min: float = Field(default=150, description="High-pass filter cutoff frequency")
    sigmaMask: float = Field(default=30, description="Spatial constant in um for computing residual variance of spike")
    nPCs: int = Field(default=3, description="Number of PCA dimensions")
    ntbuff: int = Field(default=64, description="Samples of symmetrical buffer for whitening and spike detection")
    nfilt_factor: int = Field(default=4, description="Max number of clusters per good channel (even temporary ones) 4")
    NT: int = Field(default=-1, description='Batch size (if -1 it is automatically computed)')
    AUCsplit: float = Field(default=0.9, description="Threshold on the area under the curve (AUC) criterion for performing a split in the final step")
    do_correction: bool = Field(default=False, description="If True drift registration is applied")
    wave_length: float = Field(default=61, description="size of the waveform extracted around each detected peak, (Default 61, maximum 81)")
    keep_good_only: bool = Field(default=True, description="If True only 'good' units are returned")
    skip_kilosort_preprocessing: bool = Field(default=False, description="Can optionaly skip the internal kilosort preprocessing")
    scaleproc: int = Field(default=-1, description="int16 scaling of whitened data, if -1 set to 200.")
    test_duration_sec: float = Field(default=0, description='For testing purposes: duration of the recording in seconds (0 means all)')

class Kilosort2_5HamilosLabProcessor(ProcessorBase):
    name = 'kilosort2_5-hamiloslab'
    description = 'Kilosort2_5 Hamilos Lab processor'
    label = 'Kilosort 2.5 Hamilos Lab'
    tags = ['spike_sorting', 'spike_sorter']
    attributes = {'wip': True}
    @staticmethod
    def run(context: Kilosort2_5HamilosLabContext):
        import h5py
        import remfile
        import pynwb
        from NwbRecording import NwbRecording
        from create_sorting_out_nwb_file import create_sorting_out_nwb_file
        from run_kilosort2_5 import run_kilosort2_5
        from make_int16_recording import make_int16_recording
        from print_elapsed_time import print_elapsed_time, start_timer

        print('Starting kilosort 2.5 Hamilos lab processor')
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

        sortings = []
        for group in unique_channel_groups:
            print(f'Processing group {group}')
            channel_ids_in_group = [ch for ch in recording.get_channel_ids() if recording.get_channel_property(ch, 'group') == group] # get this from recording, not recording_binary
            print(f'Channels: {channel_ids_in_group}')
            recording_group = recording_binary.channel_slice(channel_ids=channel_ids_in_group)

            # important to prepare this for kilosort
            recording_group_binary = make_int16_recording(recording_group, dirname=f'/tmp/int16_recording_group_{group}')

            print(f'Running kilosort 2.5 on group {group}')
            sorting = run_kilosort2_5(
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
