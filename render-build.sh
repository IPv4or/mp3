#!/usr/bin/env bash
# exit on error
set -e

# Install python dependencies
pip install -r requirements.txt

# Install ffmpeg
apt-get update && apt-get install -y ffmpeg
