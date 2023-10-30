from protocaas.sdk import ProcessorBase
from spikeinterface_pipelines import pipeline as si_pipeline

from .models import PipelineContext


class PipelineProcessor(ProcessorBase):
    name = 'spikeinterface_pipeline'
    label = 'SpikeInterface Pipeline'
    help = "SpikeInterface Pipeline Processor"
    tags = ['spike_interface', 'electrophysiology', 'preprocessing', 'sorting', 'postprocessing']

    @staticmethod
    def run(context: PipelineContext):

        # TODO - create SI recording from InputFile
        

        # TODO - run pipeline
        si_pipeline.pipeline(
            recording=,
            results_path="./results/",
            preprocessing_params=context.preprocessing_params,
            sorting_params=context.sorting_params,
            # postprocessing_params=context.postprocessing_params,
            # run_preprocessing=context.run_preprocessing,
        )