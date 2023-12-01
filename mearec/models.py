from dendro.sdk import BaseModel, Field, OutputFile


class MearecGenerateTemplatesContext(BaseModel):
    output: OutputFile = Field(description='Output .templates.h5 file')
