# The first instruction is what image we want to base our container on
# We Use an official Python runtime as a parent image
FROM python:3.7

# The enviroment variable ensures that the python output is set straight
# to the terminal with out buffering it first
ENV PYTHONUNBUFFERED 1

# create root directory for our project in the container
RUN mkdir /bitpoint

# Set the working directory to /bitpoint
WORKDIR /bitpoint/src

# Copy the current directory contents into the container at /bitpoint
ADD . /bitpoint/src

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt


# CREATE DB AND USER
FROM library/postgres

ENV POSTGRES_USER abdoul

ENV POSTGRES_PASSWORD bitpoint_tenants

ENV POSTGRES_DB bitpoint_tenants