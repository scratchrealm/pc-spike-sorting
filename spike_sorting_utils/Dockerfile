FROM python

RUN mkdir /src

# Install pynwb
RUN pip install pynwb

# Install spikeinterface
RUN pip install spikeinterface==0.99.1

# Install sortingview
RUN pip install sortingview==0.12.0

# Install dendro
RUN pip install dendro==0.1.14.dev.2

# Get the latest version (needed to add this line during development)
RUN pip install --upgrade kachery-cloud

# Copy files into the container
RUN mkdir /app
COPY spike_sorting_utils/*.py /app/
COPY spike_sorting_utils/helpers /app/helpers
COPY spike_sorting_utils/common /app/common
