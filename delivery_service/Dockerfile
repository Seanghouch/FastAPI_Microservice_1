# Use an official Python image from the Docker Hub
FROM python:3.11.4-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY ./app .

# Expose the port the Delivery Service will run on
EXPOSE 8000

# Command to run the Delivery Service
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
