from protocaas.sdk import ProcessorBase
from spikeinterface_pipelines import si_preprocessing

from .models import PreprocessingContext


class PreprocessingProcessor(ProcessorBase):
    name = 'spikeinterface_preprocessing'
    label = 'SpikeInterface Preprocessing'
    help = "SpikeInterface Preprocessing Processor"
    tags = ['spike_interface', 'electrophysiology', 'preprocessing']
    attributes = {
        'wip': True
    }

    @staticmethod
    def run(context: PreprocessingContext):
        """
        Run the processor.

        Args:
            context (PreprocessingContext): _description_
        """
        preprocessing_kwargs = context.preprocessing_kwargs
        nwb_obj = si_preprocessing(**preprocessing_kwargs)