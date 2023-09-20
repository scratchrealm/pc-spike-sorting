import numpy as np
import h5py
import spikeinterface as si


def NwbSorting(file: h5py.File) -> None:
    # Load unit IDs
    ids = file['units']['id'][:]

    # Load spike times index
    spike_times_index = file['units']['spike_times_index'][:]

    # Load spike times
    spike_times = file['units']['spike_times'][:]

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
    sorting = si.NumpySorting.from_dict(
        [units_dict], sampling_frequency=sampling_frequency
    )
    return sorting