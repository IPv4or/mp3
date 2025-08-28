#!/usr/bin/env bash
# exit on error
set -e

pip install -r requirements.txt

# Clean, update, and install ffmpeg
apt-get clean
apt-get update
apt-get install -y --no-install-recommends ffmpeg
