from typing import List, Optional
from dendro.sdk import BaseModel, Field, OutputFile

class IntracellularSimulationSettings(BaseModel):
    sime_time: List[float] = Field(default=[3, 50], description='Intracellular simulation time in s')
    target_spikes: List[int] = Field(default=[2, 5], description='Min-max number of spikes in sim_time')
    cut_out: List[int] = Field(default=0.03125, description='Pre-post peak cut_out in ms')
    dt: float = Field(default=10, description='Stimulation delay in ms')
    weights: List[float] = Field(default=[0.25, 1.75], description='Weights to multiply stimulus amplitude if number of spikes is above (0.25) or above (1.25) target spikes')

class ExtracellularSimulationSettings(BaseModel):
    rot: str = Field(default='physrot', description='Random rotation to apply to cell models (norot, physrot, 3drot)')
    probe: str = Field(default='Neuronexus-32', description='Extracellular probe (if None probes are listed)')
    ncontacts: int = Field(default=1, description='Number of contacts per recording site')
    overhang: int = Field(default=30, description='Extension in un beyond MEA boundaries for neuron locations (if lim is null)')
    offset: int = Field(default=0, description='Plane offset (um) for MEA')
    xlim: List[int] = Field(default=[10, 80], description='Limits ( low high ) for neuron locations in the x-axis (depth)')
    ylim: Optional[List[int]] = Field(default=None, description='Limits ( low high ) for neuron locations in the y-axis')
    zlim: Optional[List[int]] = Field(default=None, description='Limits ( low high ) for neuron locations in the z-axis')
    det_thresh: int = Field(default=30, description='Detection threshold for EAPs')
    n: int = Field(default=50, description='Number of EAPs per cell model')
    seed: Optional[int] = Field(default=None, description='Random seed for positions and rotations')

class DriftingSettings(BaseModel):
    drifting: bool = Field(default=False, description='If True, drifting templates are simulated')
    max_drift: int = Field(default=100, description='Max distance from the initial and final cell position')
    min_drift: int = Field(default=30, description='Min distance from the initial and final cell position')
    drift_steps: int = Field(default=50, description='Number of drift steps')
    drift_x_lim: List[int] = Field(default=[-10, 10], description='Drift limits in the x-direction')
    drift_y_lim: List[int] = Field(default=[-10, 10], description='Drift limits in the y-direction')
    drift_z_lim: List[int] = Field(default=[20, 80], description='Drift limits in the z-direction')

class MearecGenerateTemplatesContext(BaseModel):
    output: OutputFile = Field(default=1, description='Output .templates.h5 file')
    intracellular: IntracellularSimulationSettings = Field(description='Intracellular simulation settings')
    extracellular: ExtracellularSimulationSettings = Field(description='Extracellular simulation settings')
    drift: DriftingSettings = Field(description='Drifting settings')
