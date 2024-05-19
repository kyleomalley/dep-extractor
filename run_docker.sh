#!/bin/bash

# Build Docker image
docker build -t dep-extractor .

# Run Docker container
docker run -it -v $(pwd)/packages_dir:/app/packages_dir dep-extractor
