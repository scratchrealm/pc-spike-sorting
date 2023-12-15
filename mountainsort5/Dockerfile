FROM python

RUN mkdir /src

# Install pynwb
RUN pip install pynwb

# Install spikeinterface
RUN pip install spikeinterface==0.99.1

# Install mountainsort5
RUN pip install mountainsort5==0.3.3

# # Install dendro
# RUN pip install dendro==0.1.22

# # Install dendro from github
RUN git clone https://github.com/flatironinstitute/dendro.git /src/dendro \
    && cd /src/dendro/python \
    && git checkout use-monitoring-processes \
    && pip install -e . && echo "7"

# Copy files into the container
RUN mkdir /app
COPY mountainsort5/*.py /app/
COPY mountainsort5/common /app/common