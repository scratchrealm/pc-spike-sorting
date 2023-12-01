FROM spikeinterface/kilosort2_5-compiled-base

RUN mkdir /src

# Install pynwb
RUN pip install pynwb

# Install spikeinterface
RUN pip install spikeinterface==0.99.1

# For monitoring GPU
RUN pip install GPUtil

# Install dendro
RUN pip install dendro==0.1.18

# Copy files into the container
RUN mkdir /app
COPY kilosort2_5/*.py /app/
COPY kilosort2_5/common /app/common
