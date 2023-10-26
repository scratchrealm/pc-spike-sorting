FROM python

RUN mkdir /src

# Install protocaas from source, for now
RUN git clone https://github.com/scratchrealm/protocaas.git /src/protocaas && echo "v20" && \
    cd /src/protocaas/python && \
    pip install -e .

# Install pynwb
RUN pip install pynwb

# Install spikeinterface
RUN pip install spikeinterface

# Install sortingview
RUN pip install sortingview

# Copy files into the container
RUN mkdir /app
COPY helpers /app/helpers
COPY *.py /app/
COPY main.py /app/main.py