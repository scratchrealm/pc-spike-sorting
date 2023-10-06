import h5py
import pynwb
import remfile


# Comes from DANDI: 000409/sub-CSH-ZAD-001/sub-CSH-ZAD-001_ses-3e7ae7c0-fe8b-487c-9354-036236fa1010-chunking-27307-192_behavior+ecephys.nwb
# 000409: IBL - Brain Wide Map
nwb_url = 'https://api.dandiarchive.org/api/assets/b97bc304-e1e1-4164-91c4-ce7df98dd78f/download/'
nwb_remf = remfile.File(nwb_url)
h5_file = h5py.File(nwb_remf, 'r')

with pynwb.NWBHDF5IO(file=h5_file, mode='r', load_namespaces=True) as io:
    nwbfile_rec = io.read()
    # raises exception: KeyError: "'ndx-pose' not a namespace"