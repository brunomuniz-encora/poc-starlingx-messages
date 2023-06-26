# Use an appropriate base image for Python
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements/requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY ./src/* .

# Set PYTHONPATH - not sure why I can only set the root
ENV PYTHONPATH "/app"

# Specify the command to run when the container starts
CMD ["/app/main.py"]

