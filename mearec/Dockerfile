# Note: neuron python package is not compatible with more recent versions of python
FROM python:3.8

# Install openmpi
RUN apt-get update && apt-get install -y libopenmpi-dev

# Install LFPy
RUN pip install LFPy>=2.2

# Install mearec
RUN pip install MEArec
RUN pip install MEArec[templates]

# This creates the cell models in /root/.config/mearec/...
RUN mearec default-config

# Install dendro
RUN pip install dendro==0.1.21.dev2

# Copy files into the container
RUN mkdir /app
COPY mearec/*.py /app/