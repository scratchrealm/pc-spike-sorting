FROM python

RUN mkdir /src

# Install protocaas from source, for now
RUN git clone https://github.com/scratchrealm/protocaas.git /src/protocaas && echo "v12" && \
    cd /src/protocaas/python && \
    pip install -e .

# Install dandi
RUN pip install dandi

# Copy files into the container
RUN mkdir /app
COPY main /app/main