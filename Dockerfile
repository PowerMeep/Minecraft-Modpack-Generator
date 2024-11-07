# Use the official Python image as the base image
FROM python:3.12-slim-bullseye
EXPOSE 8000
WORKDIR /app
CMD ["python3", "main.py"]

# Expose this directory for overrides
VOLUME /app/data

# Temp build dir should always be empty
VOLUME /app/temp

# Build output directory
VOLUME /app/build

# Copy stuff over
COPY builder/ .
COPY requirements.txt .

# Set ENVs
ENV CURSEFORGE_API_KEY=""
ENV CACHE_STALE_TIME=""

# Install the application dependencies
RUN pip install -r requirements.txt
