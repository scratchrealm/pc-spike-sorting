import numpy as np
import h5py
import pynwb
import spikeinterface as si


def create_sorting_out_nwb_file_v2(*,
    recording_h5_file: h5py.File,
    sorting: si.BaseSorting,
    sorting_out_fname: str
):
    with h5py.File(sorting_out_fname, 'w') as newfile:
        copy_group(recording_h5_file, newfile)

    with pynwb.NWBHDF5IO(sorting_out_fname, 'r+', load_namespaces=True) as io: # type: ignore
        read_nwbfile = io.read()
        for ii, unit_id in enumerate(sorting.get_unit_ids()):
            st = sorting.get_unit_spike_train(unit_id) / sorting.get_sampling_frequency()
            read_nwbfile.add_unit( # type: ignore
                id=ii + 1, # must be an int
                spike_times=st
            )
        io.write(read_nwbfile) # type: ignore

def copy_group(grp: h5py.Group, newgrp: h5py.Group):
    for k, v in grp.attrs.items():
        newgrp.attrs[k] = v

    for k, v in grp.items():
        if isinstance(v, h5py.Group):
            new_subgrp = newgrp.create_group(k)
            copy_group(v, new_subgrp)
        elif isinstance(v, h5py.Dataset):
            if np.prod(v.shape) <= 10000:
                ds = newgrp.create_dataset(k, data=v[()])
            else:
                # if the dataset is large, then
                # create the dataset but don't actually copy the data
                ds = newgrp.create_dataset(k, shape=v.shape, dtype=v.dtype)
            for k2, v2 in v.attrs.items():
                ds.attrs[k2] = v2
        else:
            print(f'WARNING: skipping {k} of type {type(v)}')
