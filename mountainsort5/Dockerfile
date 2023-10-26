FROM python

RUN mkdir /src

# Install protocaas from source, for now
RUN git clone https://github.com/scratchrealm/protocaas.git /src/protocaas && echo "v20" && \
    cd /src/protocaas/python && \
    pip install -e .

# Install pynwb
RUN pip install pynwb

# Install mountainsort5
RUN pip install mountainsort5==0.3.3

# Copy files into the container
RUN mkdir /app
COPY *.py /app/
COPY main.py /app/main.py