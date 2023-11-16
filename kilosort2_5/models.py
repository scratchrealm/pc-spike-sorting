from typing import List
from dendro.sdk import BaseModel, Field, InputFile, OutputFile


class Kilsort2_5Context(BaseModel):
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
    do_correction: bool = Field(default=True, description="If True drift registration is applied")
    wave_length: float = Field(default=61, description="size of the waveform extracted around each detected peak, (Default 61, maximum 81)")
    keep_good_only: bool = Field(default=True, description="If True only 'good' units are returned")
    skip_kilosort_preprocessing: bool = Field(default=False, description="Can optionally skip the internal kilosort preprocessing")
    scaleproc: int = Field(default=-1, description="int16 scaling of whitened data, if -1 set to 200.")
    test_duration_sec: float = Field(default=0, description='For testing purposes: duration of the recording in seconds (0 means all)')
    lazy_read_input: bool = Field(default=True, description='If True (default and recommended) the input is read lazily, otherwise the entire nwb file is downloaded upfront.')

class Kilsort2_5QuicktestContext(BaseModel):
    input: InputFile = Field(description='input .nwb file')
    output: OutputFile = Field(description='output .nwb file')
    electrical_series_path: str = Field(description='Path to the electrical series in the NWB file, e.g., /acquisition/ElectricalSeries')
    test_duration_sec: float = Field(default=60, description='For testing purposes: duration of the recording in seconds (0 means all)')

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
    skip_kilosort_preprocessing: bool = Field(default=False, description="Can optionally skip the internal kilosort preprocessing")
    scaleproc: int = Field(default=-1, description="int16 scaling of whitened data, if -1 set to 200.")
    test_duration_sec: float = Field(default=0, description='For testing purposes: duration of the recording in seconds (0 means all)')
