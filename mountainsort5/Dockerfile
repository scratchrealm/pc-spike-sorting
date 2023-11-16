FROM python

RUN mkdir /src

# Install dendro from source, for now
RUN git clone https://github.com/flatironinstitute/dendro.git /src/dendro && echo "v42" && \
    cd /src/dendro/python && \
    pip install -e .

# Install pynwb
RUN pip install pynwb

# Install mountainsort5
RUN pip install mountainsort5==0.3.3

# Upgrade remfile
RUN pip install --upgrade remfile

# Copy files into the container
RUN mkdir /app
COPY mountainsort5/*.py /app/
COPY mountainsort5/common /app/common