#!/usr/bin/env python3

import os
import protocaas.sdk as pr

try:
    from typing import List
    import h5py
    import remfile
    import spikeinterface.preprocessing as spre
    from NwbRecording import NwbRecording
    from NwbSorting import NwbSorting
    import sortingview.views as vv
    from helpers.compute_correlogram_data import compute_correlogram_data
except ImportError:
    # Do not raise import error if we are only generating the spec
    if os.environ.get('PROTOCAAS_GENERATE_SPEC', None) != '1':
        raise


app = pr.App(
    'spike_sorting_utils', 
    help="Utilities for working with spike sorting data",
    app_image="magland/pc-spike-sorting-utils",
    app_executable="/app/main.py"
)

description = """
Create summary data for a spike sorting run.
"""

@pr.processor('spike_sorting_figurl', help=description)
@pr.attribute('wip', True)
@pr.attribute('label', 'Spike sorting figurl')
@pr.tags(['spike_sorting'])
@pr.input('recording', help='recording .nwb file')
@pr.input('sorting', help='sorting .nwb file')
@pr.output('output', help='output .figurl file')
@pr.parameter('electrical_series_path', type=str, help='Path to the electrical series in the recording NWB file, e.g., /acquisition/ElectricalSeries')
def spike_sorting_figurl(
    recording: pr.InputFile,
    sorting: pr.InputFile,
    output: pr.OutputFile,
    electrical_series_path: str
):
    print('Starting spike_sorting_figurl')
    recording_nwb_url = recording.get_url()
    sorting_nwb_url = sorting.get_url()
    print(f'Input recording NWB URL: {recording_nwb_url}')
    print(f'Input sorting NWB URL: {sorting_nwb_url}')

    # open the remote file
    print('Opening remote input recording file')
    # Use a disk cache because we are going to be doing random access
    disk_cache = remfile.DiskCache('/tmp/remfile_cache')
    recording_remf = remfile.File(recording_nwb_url, disk_cache=disk_cache)
    recording_f = h5py.File(recording_remf, 'r')

    print('Creating input recording')
    recording = NwbRecording(
        file=recording_f,
        electrical_series_path=electrical_series_path
    )

    print('Opening remote input sorting file')
    sorting_remf = remfile.File(sorting_nwb_url, disk_cache=disk_cache)
    sorting_f = h5py.File(sorting_remf, 'r')
    sorting = NwbSorting(file=sorting_f)

    freq_min = 300
    freq_max = 6000
    recording_filtered = spre.bandpass_filter(recording, freq_min=freq_min, freq_max=freq_max)

    print('Computing autocorrelograms')
    autocorrelogram_items: List[vv.AutocorrelogramItem] = []
    for unit_id in sorting.get_unit_ids():
        a = compute_correlogram_data(sorting=sorting, unit_id1=unit_id, unit_id2=None, window_size_msec=50, bin_size_msec=1)
        bin_edges_sec = a['bin_edges_sec']
        bin_counts = a['bin_counts']
        autocorrelogram_items.append(
            vv.AutocorrelogramItem(
                unit_id=unit_id,
                bin_edges_sec=bin_edges_sec,
                bin_counts=bin_counts
            )
        )
    view = vv.Autocorrelograms(
        autocorrelograms=autocorrelogram_items
    )
    output_url = view.url(label='Autocorrelograms')

    if not os.path.exists('output'):
        os.mkdir('output')
    output_fname = 'output/output.figurl'

    with open(output_fname, 'w') as f:
        f.write(output_url)
    
    print('Uploading output file')
    output.set(output_fname)

app.add_processor(spike_sorting_figurl)

if __name__ == '__main__':
    app.run()
