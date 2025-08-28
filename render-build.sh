#!/usr/bin/env bash
# exit on error
set -e

# Install python dependencies
pip install -r requirements.txt

# Clean, update, and install ffmpeg. This is a more robust command.
apt-get clean
apt-get update
apt-get install -y --no-install-recommends ffmpeg
