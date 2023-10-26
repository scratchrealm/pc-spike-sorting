import protocaas.sdk as pr

from .processor_preprocessing import PreprocessingProcessor
from .processor_sorting import SortingProcessor
from .processor_postprocessing import PostprocessingProcessor
from .processor_curation import CurationProcessor
from .processor_pipeline import PipelineProcessor


app = pr.App(
    'spikeinterface', 
    help="Spike Interface",
    app_image="magland/spikeinterface",
    app_executable="/app/main.py"
)


app.add_processor(PreprocessingProcessor)
app.add_processor(SortingProcessor)
app.add_processor(PostprocessingProcessor)
app.add_processor(CurationProcessor)
app.add_processor(PipelineProcessor)


if __name__ == '__main__':
    app.run()
