FROM python

# Install openmpi
RUN apt-get update && apt-get install -y libopenmpi-dev

# Install LFPy
RUN pip install LFPy>=2.2

# Install mearec
RUN pip install MEArec
RUN pip install MEArec[templates]

# Install dendro
RUN pip install dendro==0.1.18

# Copy files into the container
RUN mkdir /app
COPY mearec/*.py /app/