from protocaas.sdk import field, InputFile, OutputFile
from dataclasses import dataclass



# ------------------------------
# Preprocessing Models
# ------------------------------
@dataclass
class HighpassFilter:
    freq_min: float = field(default=300.0, help="Minimum frequency for the highpass filter")
    margin_ms: float = field(default=5.0, help="Margin in milliseconds")


@dataclass
class PhaseShift:
    margin_ms: float = field(default=100.0, help="Margin in milliseconds for phase shift")


@dataclass
class DetectBadChannels:
    method: str = field(default="coherence+psd", help="Method to detect bad channels")
    dead_channel_threshold: float = field(default=-0.5, help="Threshold for dead channel")
    noisy_channel_threshold: float = field(default=1.0, help="Threshold for noisy channel")
    outside_channel_threshold: float = field(default=-0.3, help="Threshold for outside channel")
    n_neighbors: int = field(default=11, help="Number of neighbors")
    seed: int = field(default=0, help="Seed value")


@dataclass
class CommonReference:
    reference: str = field(default="global", help="Type of reference")
    operator: str = field(default="median", help="Operator used for common reference")


@dataclass
class HighpassSpatialFilter:
    n_channel_pad: int = field(default=60, help="Number of channels to pad")
    n_channel_taper: Optional[int] = field(default=None, help="Number of channels to taper")
    direction: str = field(default="y", help="Direction for the spatial filter")
    apply_agc: bool = field(default=True, help="Whether to apply automatic gain control")
    agc_window_length_s: float = field(default=0.01, help="Window length in seconds for AGC")
    highpass_butter_order: int = field(default=3, help="Order for the Butterworth filter")
    highpass_butter_wn: float = field(default=0.01, help="Natural frequency for the Butterworth filter")


@dataclass
class PreprocessingModel:
    highpass_filter: HighpassFilter
    phase_shift: PhaseShift
    detect_bad_channels: DetectBadChannels
    common_reference: CommonReference
    highpass_spatial_filter: HighpassSpatialFilter
    preprocessing_strategy: str = field(default="cmr", help="Strategy for preprocessing")
    remove_out_channels: bool = field(default=False, help="Flag to remove out channels")
    remove_bad_channels: bool = field(default=False, help="Flag to remove bad channels")
    max_bad_channel_fraction_to_remove: float = field(default=1.1, help="Maximum fraction of bad channels to remove")


@dataclass
class PreprocessingContext:
    input: InputFile = field(help='Input NWB file')
    output: OutputFile = field(help='Output NWB file')
    preprocessing_kwargs: PreprocessingModel = field(help='Preprocessing parameters')


# ------------------------------
# Sorter Models
# ------------------------------
@dataclass
class SortingContext:
    pass 


# ------------------------------
# Postprocessing Models
# ------------------------------
@dataclass
class PostprocessingContext:
    pass


# ------------------------------
# Curation Models
# ------------------------------
@dataclass
class CurationContext:
    pass


# ------------------------------
# Pipeline Models
# ------------------------------
@dataclass
class PipelineContext:
    preprocessing_context: PreprocessingContext
    sorting_context: SortingContext
    postprocessing_context: PostprocessingContext
    curation_context: CurationContext


# # ------------------------------
# # Sorter Models
# # ------------------------------
# class SorterName(str, Enum):
#     ironclust = "ironclust"
#     kilosort2 = "kilosort2"
#     kilosort25 = "kilosort25"
#     kilosort3 = "kilosort3"
#     spykingcircus = "spykingcircus"


# class SorterKwargs:
#     sorter_name: SorterName = field(help="Name of the sorter to use.")


# # ------------------------------
# # Postprocessing Models
# # ------------------------------
# class PresenceRatio:
#     bin_duration_s: float = field(default=60, help="Duration of the bin in seconds.")


# class SNR:
#     peak_sign: str = field(default="neg", help="Sign of the peak.")
#     peak_mode: str = field(default="extremum", help="Mode of the peak.")
#     random_chunk_kwargs_dict: Optional[dict] = field(default=None, help="Random chunk arguments.")


# class ISIViolation:
#     isi_threshold_ms: float = field(default=1.5, help="ISI threshold in milliseconds.")
#     min_isi_ms: float = field(default=0., help="Minimum ISI in milliseconds.")


# class RPViolation:
#     refractory_period_ms: float = field(default=1., help="Refractory period in milliseconds.")
#     censored_period_ms: float = field(default=0.0, help="Censored period in milliseconds.")


# class SlidingRPViolation:
#     min_spikes: int = field(default=0, help="Contamination is set to np.nan if the unit has less than this many spikes across all segments.")
#     bin_size_ms: float = field(default=0.25, help="The size of binning for the autocorrelogram in ms, by default 0.25.")
#     window_size_s: float = field(default=1, help="Window in seconds to compute correlogram, by default 1.")
#     exclude_ref_period_below_ms: float = field(default=0.5, help="Refractory periods below this value are excluded, by default 0.5")
#     max_ref_period_ms: float = field(default=10, help="Maximum refractory period to test in ms, by default 10 ms.")
#     contamination_values: Optional[list] = field(default=None, help="The contamination values to test, by default np.arange(0.5, 35, 0.5) %")


# class PeakSign(str, Enum):
#     neg = "neg"
#     pos = "pos"
#     both = "both"


# class AmplitudeCutoff:
#     peak_sign: PeakSign = field(default="neg", help="The sign of the peaks.")
#     num_histogram_bins: int = field(default=100, help="The number of bins to use to compute the amplitude histogram.")
#     histogram_smoothing_value: int = field(default=3, help="Controls the smoothing applied to the amplitude histogram.")
#     amplitudes_bins_min_ratio: int = field(default=5, help="The minimum ratio between number of amplitudes for a unit and the number of bins. If the ratio is less than this threshold, the amplitude_cutoff for the unit is set to NaN.")


# class AmplitudeMedian:
#     peak_sign: PeakSign = field(default="neg", help="The sign of the peaks.")


# class NearestNeighbor:
#     max_spikes: int = field(default=10000, help="The number of spikes to use, per cluster. Note that the calculation can be very slow when this number is >20000.")
#     min_spikes: int = field(default=10, help="Minimum number of spikes.")
#     n_neighbors: int = field(default=4, help="The number of neighbors to use.")


# class NNIsolation(NearestNeighbor):
#     n_components: int = field(default=10, help="The number of PC components to use to project the snippets to.")
#     radius_um: int = field(default=100, help="The radius, in um, that channels need to be within the peak channel to be included.")


# class QMParams:
#     presence_ratio: PresenceRatio
#     snr: SNR
#     isi_violation: ISIViolation
#     rp_violation: RPViolation
#     sliding_rp_violation: SlidingRPViolation
#     amplitude_cutoff: AmplitudeCutoff
#     amplitude_median: AmplitudeMedian
#     nearest_neighbor: NearestNeighbor
#     nn_isolation: NNIsolation
#     nn_noise_overlap: NNIsolation


# class QualityMetrics:
#     qm_params: QMParams = field(help="Quality metric parameters.")
#     metric_names: List[str] = field(help="List of metric names to compute.")
#     n_jobs: int = field(default=1, help="Number of jobs.")


# class Sparsity:
#     method: str = field("radius", help="Method for determining sparsity.")
#     radius_um: int = field(100, help="Radius in micrometers for sparsity.")


# class Waveforms:
#     ms_before: float = field(3.0, help="Milliseconds before")
#     ms_after: float = field(4.0, help="Milliseconds after")
#     max_spikes_per_unit: int = field(500, help="Maximum spikes per unit")
#     return_scaled: bool = field(True, help="Flag to determine if results should be scaled")
#     dtype: Optional[str] = field(None, help="Data type for the waveforms")
#     precompute_template: Tuple[str, str] = field(("average", "std"), help="Precomputation template method")
#     use_relative_path: bool = field(True, help="Use relative paths")


# class SpikeAmplitudes:
#     peak_sign: str = field("neg", help="Sign of the peak")
#     return_scaled: bool = field(True, help="Flag to determine if amplitudes should be scaled")
#     outputs: str = field("concatenated", help="Output format for the spike amplitudes")


# class Similarity:
#     method: str = field("cosine_similarity", help="Method to compute similarity")


# class Correlograms:
#     window_ms: float = field(100.0, help="Size of the window in milliseconds")
#     bin_ms: float = field(2.0, help="Size of the bin in milliseconds")


# class ISIS:
#     window_ms: float = field(100.0, help="Size of the window in milliseconds")
#     bin_ms: float = field(5.0, help="Size of the bin in milliseconds")


# class Locations:
#     method: str = field("monopolar_triangulation", help="Method to determine locations")


# class TemplateMetrics:
#     upsampling_factor: int = field(10, help="Upsampling factor")
#     sparsity: Optional[str] = field(None, help="Sparsity method")


# class PrincipalComponents:
#     n_components: int = field(5, help="Number of principal components")
#     mode: str = field("by_channel_local", help="Mode of principal component analysis")
#     whiten: bool = field(True, help="Whiten the components")


# class PostprocessingKwargs:
#     sparsity: Sparsity
#     waveforms_deduplicate: Waveforms
#     waveforms: Waveforms
#     spike_amplitudes: SpikeAmplitudes
#     similarity: Similarity
#     correlograms: Correlograms
#     isis: ISIS
#     locations: Locations
#     template_metrics: TemplateMetrics
#     principal_components: PrincipalComponents
#     quality_metrics: QualityMetrics


# # ------------------------------
# # Curation Models
# # ------------------------------
# class CurationKwargs:
#     duplicate_threshold: float = field(0.9, help="Threshold for duplicate units")
#     isi_violations_ratio_threshold: float = field(0.5, help="Threshold for ISI violations ratio")
#     presence_ratio_threshold: float = field(0.8, help="Threshold for presence ratio")
#     amplitude_cutoff_threshold: float = field(0.1, help="Threshold for amplitude cutoff")


# # ------------------------------
# # Visualization Models
# # ------------------------------
# class Timeseries:
#     n_snippets_per_segment: int = field(2, help="Number of snippets per segment")
#     snippet_duration_s: float = field(0.5, help="Duration of the snippet in seconds")
#     skip: bool = field(False, help="Flag to skip")


# class Detection:
#     method: str = field("locally_exclusive", help="Method for detection")
#     peak_sign: str = field("neg", help="Sign of the peak")
#     detect_threshold: int = field(5, help="Detection threshold")
#     exclude_sweep_ms: float = field(0.1, help="Exclude sweep in milliseconds")


# class Localization:
#     ms_before: float = field(0.1, help="Milliseconds before")
#     ms_after: float = field(0.3, help="Milliseconds after")
#     local_radius_um: float = field(100.0, help="Local radius in micrometers")


# class Drift:
#     detection: Detection
#     localization: Localization
#     n_skip: int = field(30, help="Number of skips")
#     alpha: float = field(0.15, help="Alpha value")
#     vmin: int = field(-200, help="Minimum value")
#     vmax: int = field(0, help="Maximum value")
#     cmap: str = field("Greys_r", help="Colormap")
#     figsize: Tuple[int, int] = field((10, 10), help="Figure size")


# class VisualizationKwargs:
#     timeseries: Timeseries
#     drift: Drift
