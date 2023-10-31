FROM python

RUN mkdir /src

# Install dendro from source, for now
RUN git clone https://github.com/flatironinstitute/dendro.git /src/dendro && echo "v24" && \
    cd /src/dendro/python && \
    pip install -e .

# Install dandi
RUN pip install dandi

# Copy files into the container
RUN mkdir /app
COPY main.py /app/main