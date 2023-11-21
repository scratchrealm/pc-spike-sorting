#!/usr/bin/env python3

import os
from typing import List
import json
import shutil
import subprocess
from dendro.sdk import App, ProcessorBase, BaseModel, Field, InputFile


app = App(
    'dandi_upload',
    description="Upload files to DANDI",
    app_image="ghcr.io/scratchrealm/pc-dandi_upload:latest",
    app_executable="/app/main.py"
)

description = """
Upload files to a dandiset on DANDI.
"""

class DandiUploadContext(BaseModel):
    inputs: List[InputFile] = Field(description='List of files to upload')
    dandiset_id: str = Field(description='Dandiset ID')
    dandi_instance: str = Field(default='dandi', description='dandi or dandi-staging')
    dandi_api_key: str = Field(description='DANDI API key', json_schema_extra={'secret': True})
    names: List[str] = Field(description='Destination names in the dandiset')
    was_generated_by_jsons: List[str] = Field(description='The JSON strings containing the wasGeneratedBy metadata for each input file')

class DandiUploadProcessor(ProcessorBase):
    name = 'dandi_upload'
    description = description
    label = 'DANDI upload'
    tags = ['dandi']
    attributes = {'wip': True}
    @staticmethod
    def run(context: DandiUploadContext):
        print('Starting dandi_upload')

        if len(context.inputs) != len(context.names):
            raise Exception('Number of inputs does not match number of names')
        if len(context.inputs) == 0:
            raise Exception('No inputs')
        if not context.dandiset_id:
            raise Exception('dandiset_id is required')
        if not context.dandi_instance:
            raise Exception('dandi_instance is required')
        if not context.dandi_api_key:
            raise Exception('dandi_api_key is required')

        if context.dandi_instance == 'dandi':
            dandi_archive_url = 'https://dandiarchive.org'
        elif context.dandi_instance == 'dandi-staging':
            dandi_archive_url = 'https://gui-staging.dandiarchive.org'
        else:
            raise Exception(f'Unexpected dandi_instance: {context.dandi_instance}')

        dandiset_version = 'draft' # always going to be draft for uploading
        workdir = context.dandiset_id

        try:
            cmd = f'dandi download --dandi-instance {context.dandi_instance} --download dandiset.yaml {dandi_archive_url}/dandiset/{context.dandiset_id}/{dandiset_version}'
            print(f'Running command: {cmd}')
            env = {**os.environ, 'DANDI_API_KEY': context.dandi_api_key}
            result = subprocess.run(cmd, shell=True, env=env)
            if result.returncode != 0:
                raise Exception(f'Error running dandi download: {result.stderr}')

            for ii, inp in enumerate(context.inputs):
                name = context.names[ii]
                _make_sure_path_is_relative_and_is_safe(name)
                dest_path = os.path.join(workdir, name)
                # just to be extra safe, make sure dest_path is truly a subpath of workdir
                if not os.path.abspath(dest_path).startswith(os.path.abspath(workdir)):
                    raise Exception(f'Unexpected error: dest_path is not a subpath of workdir: {dest_path}')
                print(f'Downloading input file {ii + 1} of {len(context.inputs)} to {name}')
                # make sure parent directories of dest_path exist
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                inp.download(dest_path)

                print('Uploading file to DANDI')
                # skip validation for now, but we'll want to support this later
                cmd = f'dandi upload --dandi-instance {context.dandi_instance} --validation skip'
                print('Running command: ' + cmd)
                result = subprocess.run(cmd, shell=True, env=env, cwd=workdir)
                if result.returncode != 0:
                    raise Exception(f'Error running dandi upload: {result.stderr}')

                # set the wasGeneratedBy metadata
                _set_was_generated_by(
                    file_path=name,
                    was_generated_by_json=context.was_generated_by_jsons[ii],
                    staging=context.dandi_instance == 'dandi-staging',
                    dandiset_id=context.dandiset_id,
                    dandiset_version=dandiset_version,
                    dandi_api_key=context.dandi_api_key
                )

                # remove the file
                os.remove(dest_path)
        finally:
            shutil.rmtree(workdir)

def _set_was_generated_by(
    file_path: str,
    was_generated_by_json: str,
    staging: bool,
    dandiset_id: str,
    dandiset_version: str,
    dandi_api_key: str
):
    import requests
    headers = {
        'Authorization': f'token {dandi_api_key}'
    }
    assets_base_url = f'https://api{"-staging" if staging else ""}.dandiarchive.org/api/dandisets/{dandiset_id}/versions/{dandiset_version}/assets'
    assets_url = f'{assets_base_url}/?path={file_path}'

    # Get the asset from the dandi api
    res = requests.get(assets_url, headers=headers)
    if res.status_code != 200:
        print(res.status_code)
        print(res.json())
        raise Exception('Failed to get assets')
    assets = res.json()['results']
    if len(assets) == 0:
        print('Asset not found')
        return
    if len(assets) > 1:
        print('More than one asset found')
    asset = assets[0]

    # Get the asset metadata from the dandi api
    asset_url = f'{assets_base_url}/{asset["asset_id"]}/'
    res = requests.get(asset_url, headers=headers)
    if res.status_code != 200:
        print(res.status_code)
        print(res.json())
        raise Exception('Failed to get metadata for asset')
    metadata = res.json()

    # Add the wasGeneratedBy metadata
    x = metadata['wasGeneratedBy']
    x.append(json.loads(was_generated_by_json))

    # Replace the asset with a new asset with the updated metadata
    put_json = {
        "blob_id": asset["blob"],
        "metadata": metadata
    }
    res = requests.put(asset_url, headers=headers, json=put_json)
    if res.status_code != 200:
        print(res.status_code)
        print(res.json())
        raise Exception('Failed to update metadata for asset')

def _make_sure_path_is_relative_and_is_safe(path):
    if path.startswith('/'):
        raise Exception('Path cannot start with /')
    components = path.split('/')
    for comp in components:
        if comp == '.':
            raise Exception('Path cannot contain .')
        if comp == '..':
            raise Exception('Path cannot contain ..')
        if comp == '':
            raise Exception('Path cannot contain empty component')

app.add_processor(DandiUploadProcessor)

if __name__ == '__main__':
    app.run()
