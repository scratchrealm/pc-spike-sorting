FROM python

RUN mkdir /src

# Install dendro from source, for now
RUN git clone https://github.com/flatironinstitute/dendro.git /src/dendro && echo "v24" && \
    cd /src/dendro/python && \
    pip install -e .

# Install pynwb
RUN pip install pynwb

# Install mountainsort5
RUN pip install mountainsort5==0.3.3

# Copy files into the container
RUN mkdir /app
COPY *.py /app/
COPY main.py /app/main.py