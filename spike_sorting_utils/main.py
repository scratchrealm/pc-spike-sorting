#!/usr/bin/env python3

import os
from typing import List
from dendro.sdk import App, ProcessorBase, BaseModel, Field, InputFile, OutputFile


app = App(
    'spike_sorting_utils',
    description="Utilities for working with spike sorting data",
    app_image="ghcr.io/scratchrealm/pc-spike_sorting_utils:latest",
    app_executable="/app/main.py"
)

description = """
Create summary data for a spike sorting run.
"""

class SpikeSortingFigurlContext(BaseModel):
    recording: InputFile = Field(description='recording .nwb file')
    sorting: InputFile = Field(description='sorting .nwb file')
    output: OutputFile = Field(description='output .figurl file')
    electrical_series_path: str = Field(description='Path to the electrical series in the recording NWB file, e.g., /acquisition/ElectricalSeries')


class SpikeSortingFigurlProcessor(ProcessorBase):
    name = 'spike_sorting_figurl'
    description = description
    label = 'Spike sorting figurl'
    tags = ['spike_sorting']
    attributes = {'wip': True}
    @staticmethod
    def run(context: SpikeSortingFigurlContext):
        import remfile
        # from common.NwbRecording import NwbRecording
        from common.NwbSorting import NwbSorting
        import sortingview.views as vv
        from helpers.compute_correlogram_data import compute_correlogram_data

        print('Starting spike_sorting_figurl')
        recording_nwb_url = context.recording.get_url()
        sorting_nwb_url = context.sorting.get_url()
        print(f'Input recording NWB URL: {recording_nwb_url}')
        print(f'Input sorting NWB URL: {sorting_nwb_url}')

        # open the remote file
        print('Opening remote input recording file')
        # Use a disk cache because we are going to be doing random access
        # disk_cache = remfile.DiskCache('/tmp/remfile_cache')
        # recording_remf = remfile.File(recording_nwb_url, disk_cache=disk_cache)
        # recording_f = h5py.File(recording_remf, 'r')

        # print('Creating input recording')
        # nwb_recording = NwbRecording(
        #     file=recording_f,
        #     electrical_series_path=context.electrical_series_path
        # )

        print('Opening remote input sorting file')
        sorting_remf = remfile.File(sorting_nwb_url)
        nwb_sorting = NwbSorting(sorting_remf)

        # freq_min = 300
        # freq_max = 6000
        # recording_filtered = spre.bandpass_filter(nwb_recording, freq_min=freq_min, freq_max=freq_max)

        print('Computing autocorrelograms')
        autocorrelogram_items: List[vv.AutocorrelogramItem] = []
        for unit_id in nwb_sorting.get_unit_ids():
            a = compute_correlogram_data(sorting=nwb_sorting, unit_id1=unit_id, unit_id2=None, window_size_msec=50, bin_size_msec=1)
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
        context.output.set(output_fname)


app.add_processor(SpikeSortingFigurlProcessor)


if __name__ == '__main__':
    app.run()
