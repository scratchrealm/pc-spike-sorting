import numpy as np
import h5py
import spikeinterface as si


def NwbSorting(file):
    h5_file = h5py.File(file, 'r')

    # Load unit IDs
    ids: np.ndarray = h5_file['units']['id'][:] # type: ignore

    # Load spike times index
    spike_times_index: np.ndarray = h5_file['units']['spike_times_index'][:] # type: ignore

    # Load spike times
    spike_times: np.ndarray = h5_file['units']['spike_times'][:] # type: ignore

    start_time_sec = np.min(spike_times)
    end_time_sec = np.max(spike_times)
    print(f'Start time (sec): {start_time_sec}')
    print(f'End time (sec): {end_time_sec}')
    units_dict = {}
    sampling_frequency = 30000 # TODO: get this from the NWB file
    for i in range(len(ids)):
        if i == 0:
            s = spike_times[0:spike_times_index[0]]
        else:
            s = spike_times[spike_times_index[i - 1]:spike_times_index[i]]
        units_dict[ids[i]] = (s * sampling_frequency).astype(np.int32)
    sorting = _numpy_sorting_from_dict([units_dict], sampling_frequency=sampling_frequency)
    return sorting

def _numpy_sorting_from_dict(units_dict_list, *, sampling_frequency):
    try:
        # different versions of spikeinterface
        # see: https://github.com/SpikeInterface/spikeinterface/issues/2083
        sorting = si.NumpySorting.from_dict(
            units_dict_list, sampling_frequency=sampling_frequency # type: ignore
        )
    except: # noqa
        sorting = si.NumpySorting.from_unit_dict(
            units_dict_list, sampling_frequency=sampling_frequency # type: ignore
        )
    return sorting
