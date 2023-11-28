FROM python

RUN mkdir /src

# Install dandi
RUN pip install dandi==0.58.0

# Install dendro
RUN pip install dendro==0.1.14.dev.3

# Copy files into the container
RUN mkdir /app
COPY dandi_upload/*.py /app/
