# Use the official Python image as the base image
FROM python:3.12-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Expose this directory for overrides
VOLUME /app/data

# Copy the application files into the working directory
COPY builder/ .
COPY requirements.txt .

# Install the application dependencies
RUN apt-get update && apt-get upgrade -y
RUN pip install -r requirements.txt

ENV CURSEFORGE_API_KEY=""
ENV CACHE_STALE_TIME=""

# Define the entry point for the container
CMD ["python3", "main.py"]

# This mostly just documents that this image will need this port exposed by the end user
EXPOSE 8000