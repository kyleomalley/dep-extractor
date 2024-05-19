# Use an official Debian runtime as a parent image
FROM debian:latest

# Install necessary tools
RUN apt-get update && \
    apt-get install -y dpkg python3 rpm

# Set the working directory
WORKDIR /packages

# Copy the script into the container
COPY dep_extractor.py /packages/

# Make the script executable
RUN chmod +x /packages/dep_extractor.py

# Command to run the script
CMD ["python3", "/packages/dep_extractor.py"]
