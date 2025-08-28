#!/usr/bin/env bash
# exit on error
set -e

pip install -r requirements.txt

# Install ffmpeg without sudo
apt-get update && apt-get install -y ffmpeg
