# Use an official Debian runtime as a parent image
FROM debian:latest

# Install necessary tools
RUN apt-get update && \
    apt-get install -y rpm dpkg

# Set the working directory
WORKDIR /packages

# Copy the script into the container
COPY extract_dependencies.py /packages/

# Make the script executable
RUN chmod +x /packages/extract_dependencies.py

# Command to run the script
CMD ["python3", "/packages/package_extractor.py"]