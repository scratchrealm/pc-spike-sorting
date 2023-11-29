from dendro.sdk import BaseModel, Field, InputFile, OutputFile


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

class Mountainsort5ProcessorContext(BaseModel):
    input: InputFile = Field(description='Input NWB file')
    output: OutputFile = Field(description='Output NWB file')
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
