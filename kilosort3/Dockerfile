FROM spikeinterface/kilosort3-compiled-base

RUN mkdir /src

# Install dendro from source, for now
RUN git clone https://github.com/flatironinstitute/dendro.git /src/dendro && echo "v32" && \
    cd /src/dendro/python && \
    git checkout pydantic-method && \
    pip install -e .

# Install pynwb
RUN pip install pynwb

# Install spikeinterface
RUN pip install spikeinterface

# Copy files into the container
RUN mkdir /app
COPY *.py /app/
COPY main.py /app/main.py