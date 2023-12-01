from typing import List, Optional
from dendro.sdk import BaseModel, Field, OutputFile


class IntracellularSettings(BaseModel):
    sim_time: float = Field(default=1, description='Intracellular simulation time in s')
    target_spikes: List[int] = Field(default=[3, 50], description='min-max number of spikes in sim_time')
    cut_out: List[int] = Field(default=[2, 5], description='pre-post peak cut_out in ms')
    dt: float = Field(default=0.03125, description='time step (2**-5) in ms')
    delay: float = Field(default=10, description='stimulation delay in ms')
    weights: List[float] = Field(default=[0.25, 1.75], description='weights to multiply stimulus amplitude if number of spikes is above (0.25) or above (1.25) target spikes')

class ExtracellularSettings(BaseModel):
    rot: str = Field(default='physrot', description='random rotation to apply to cell models (norot, physrot, 3drot)')
    probe: str = Field(default='Neuronexus-32', description='extracellular probe (if None probes are listed)')
    ncontacts: int = Field(default=1, description='number of contacts per recording site')
    overhang: float = Field(default=30, description='extension in un beyond MEA boundaries for neuron locations (if lim is null)')
    offset: float = Field(default=0, description='plane offset (um) for MEA')
    xlim: List[int] = Field(default=[10, 80], description='limits ( low high ) for neuron locations in the x-axis (depth)')
    ylim: Optional[List[int]] = Field(default=None, description='limits ( low high ) for neuron locations in the y-axis')
    zlim: Optional[List[int]] = Field(default=None, description='limits ( low high ) for neuron locations in the z-axis')
    det_thresh: float = Field(default=30, description='detection threshold for EAPs')
    n: int = Field(default=50, description='number of EAPs per cell model')
    seed: Optional[int] = Field(default=None, description='random seed for positions and rotations')

class DriftingSettings(BaseModel):
    drifting: bool = Field(default=False, description='if True, drifting templates are simulated')
    max_drift: float = Field(default=100, description='max distance from the initial and final cell position')
    min_drift: float = Field(default=30, description='min distance from the initial and final cell position')
    drift_steps: int = Field(default=50, description='number of drift steps')
    drift_x_lim: List[int] = Field(default=[-10, 10], description='drift limits in the x-direction')
    drift_y_lim: List[int] = Field(default=[-10, 10], description='drift limits in the y-direction')
    drift_z_lim: List[int] = Field(default=[20, 80], description='drift limits in the z-direction')

class MearecGenerateTemplatesContext(BaseModel):
    output: OutputFile = Field(description='Output .templates.h5 file')
    intracellular: IntracellularSettings = Field(description='Intracellular simulation settings')
    extracellular: ExtracellularSettings = Field(description='Extracellular simulation settings')
    drift: DriftingSettings = Field(description='Drifting settings')
