#!/usr/bin/env python3

import os
from dendro.sdk import App, ProcessorBase
from models import MearecGenerateTemplatesContext


description = 'Fast and customuzable biophysical simulation of extracellular recordings.'

app = App(
    'mearec',
    description=description,
    app_image="ghcr.io/scratchrealm/pc-mearec:latest",
    app_executable="/app/main.py"
)

class MearecGenerateTemplatesProcessor(ProcessorBase):
    name = 'mearec_generate_templates'
    label = 'MEArec generate templates'
    description = 'Generate templates for use in MEArec simulations'
    tags = ['spike_sorting', 'mearec_generate_templates']
    attributes = {
    }

    @staticmethod
    def run(context: MearecGenerateTemplatesContext):
        import MEArec as mr
        from print_elapsed_time import print_elapsed_time, start_timer

        output = context.output

        print('Starting MEArec generate templates')
        start_timer()

        home_dir = os.path.expanduser('~')
        cell_models_folder = f'{home_dir}/.config/mearec/1.9.0/cell_models/bbp'

        print('Generating templates')
        tempgen = mr.gen_templates(
            cell_models_folder=cell_models_folder,
            params=None,
            templates_tmp_folder=None,
            intraonly=False,
            parallel=True,
            recompile=False,
            n_jobs=None,
            delete_tmp=True,
            verbose=True
        )
        print_elapsed_time()

        print('Saving template generator')
        output_fname = 'output.templates.h5'
        mr.save_template_generator(tempgen, output_fname)
        print_elapsed_time()

        print('Uploading output file')
        output.upload(output_fname)
        print_elapsed_time()

app.add_processor(MearecGenerateTemplatesProcessor)

if __name__ == '__main__':
    app.run()
