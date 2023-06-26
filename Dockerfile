# Use an appropriate base image for Python
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements/requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
# Copies everything without the file structure so we don't need
# to even set the PYTHONPATH and just go with the flow
COPY ./src/* .

# Specify the command to run when the container starts
CMD ["/app/main.py"]

