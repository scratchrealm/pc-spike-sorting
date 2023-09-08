FROM python

RUN mkdir /src

# Install protocaas from source, for now
RUN git clone https://github.com/scratchrealm/protocaas.git /src/protocaas && \
    cd /src/protocaas/python && \
    pip install -e .

# Install mountainsort5
RUN pip install mountainsort5

# Install pynwb
RUN pip install pynwb

# Copy files into the container
RUN mkdir /app
COPY *.py /app/
COPY main /app/main