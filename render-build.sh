#!/usr/bin/env bash
# exit on error
set -e

# Install python dependencies
pip install -r requirements.txt

# Install ffmpeg using sudo for permissions
sudo apt-get update && sudo apt-get install -y ffmpeg
