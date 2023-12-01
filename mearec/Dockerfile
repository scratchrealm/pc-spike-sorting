FROM python

# Install mearec
RUN pip install MEArec
RUN pip install MEArec[templates]

# Install LFPy
RUN pip install LFPy>=2.2

# Copy files into the container
RUN mkdir /app
COPY mountainsort5/*.py /app/