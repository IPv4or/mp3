# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies, including ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container
COPY . .

# Make port 10000 available to the world outside this container
EXPOSE 10000

# Define environment variable
ENV NAME World

# Run app.py when the container launches
# Use gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
