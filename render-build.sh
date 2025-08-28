#!/usr/bin/env bash
# exit on error
set -e

# Install python dependencies
pip install -r requirements.txt

# Forcefully remove any existing lock files, clean, update, and then install ffmpeg.
rm -f /var/lib/dpkg/lock-frontend
rm -f /var/cache/apt/archives/lock
apt-get clean
apt-get update
apt-get install -y --no-install-recommends ffmpeg
