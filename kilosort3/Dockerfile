FROM spikeinterface/kilosort3-compiled-base

RUN mkdir /src

# Install protocaas from source, for now
RUN git clone https://github.com/scratchrealm/protocaas.git /src/protocaas && echo "v9" && \
    cd /src/protocaas/python && \
    pip install -e .

# Install pynwb
RUN pip install pynwb

# Install spikeinterface
RUN pip install spikeinterface

# Copy files into the container
RUN mkdir /app
COPY *.py /app/
COPY main /app/main