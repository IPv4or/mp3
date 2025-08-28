#!/usr/bin/env bash
# exit on error
set -e

# Install python dependencies
pip install -r requirements.txt

# Install ffmpeg
apt-get update && apt-get install -y ffmpeg

# Create the directories on the persistent disk if they don't exist
# The Python app also does this, but it's good practice for the build script to handle it.
mkdir -p /data/downloads

# Copy the initial cookies.txt from your repo to the persistent disk
# This will only happen once when the disk is first created.
if [ ! -f /data/cookies.txt ]; then
  cp cookies.txt /data/cookies.txt
fi
