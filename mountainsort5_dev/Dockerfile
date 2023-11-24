FROM python

RUN mkdir /src

# Install pynwb
RUN pip install pynwb

# Install spikeinterface
RUN pip install spikeinterface==0.99.1

# Install mountainsort5
RUN pip install mountainsort5==0.3.3

# Install dendro
RUN pip install dendro==0.1.14.dev.1

# Copy files into the container
RUN mkdir /app
COPY mountainsort5_dev/*.py /app/
COPY mountainsort5_dev/common /app/common