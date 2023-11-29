FROM spikeinterface/kilosort3-compiled-base

RUN mkdir /src

# Install pynwb
RUN pip install pynwb

# Install spikeinterface
RUN pip install spikeinterface==0.99.1

# For monitoring GPU
RUN pip install GPUtil

# Install dendro
RUN pip install dendro==0.1.15.dev.2

# Copy files into the container
RUN mkdir /app
COPY kilosort3/*.py /app/
COPY kilosort3/common /app/common
