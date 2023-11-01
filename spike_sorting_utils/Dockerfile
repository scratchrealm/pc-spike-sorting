FROM python

RUN mkdir /src

# Install dendro from source, for now
RUN git clone https://github.com/flatironinstitute/dendro.git /src/dendro && echo "v40" && \
    cd /src/dendro/python && \
    pip install -e .

# Install pynwb
RUN pip install pynwb

# Install spikeinterface
RUN pip install spikeinterface

# Install sortingview
RUN pip install sortingview

# Upgrade remfile
RUN pip install --upgrade remfile

# Copy files into the container
RUN mkdir /app
COPY helpers /app/helpers
COPY *.py /app/
COPY main.py /app/main.py