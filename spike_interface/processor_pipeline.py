from protocaas.sdk import ProcessorBase

from .models import PipelineContext
from .processor_preprocessing import PreprocessingProcessor
from .processor_sorting import SortingProcessor
from .processor_postprocessing import PostprocessingProcessor
from .processor_curation import CurationProcessor


class PipelineProcessor(ProcessorBase):
    name = 'spikeinterface_pipeline'
    label = 'SpikeInterface Pipeline'
    help = "SpikeInterface Pipeline Processor"
    tags = ['spike_interface', 'electrophysiology', 'preprocessing', 'sorting', 'postprocessing']

    @staticmethod
    def run(context: PipelineContext):

        # Preprocessing
        preprocessing_context = PipelineContext.preprocessing_context
        preprocessing_context.output = "nwb_object"
        output_file = PreprocessingProcessor.run(context=preprocessing_context)

        # Sorting
        sorting_context = PipelineContext.sorting_context
        sorting_context.input = output_file
        sorting_context.output = "nwb_object"
        output_file = SortingProcessor.run(context=sorting_context)

        # Postprocessing
        postprocessing_context = PipelineContext.postprocessing_context
        postprocessing_context.input = output_file
        postprocessing_context.output = "nwb_object"
        output_file = PostprocessingProcessor.run(context=postprocessing_context)

        # Curation
        curation_context = PipelineContext.curation_context
        curation_context.input = output_file
        curation_context.output = "upload"
        CurationProcessor.run(context=curation_context)