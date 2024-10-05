# Dockerfile

# Use the official Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY app/ ./app/
COPY run.py ./

# Expose the port
EXPOSE 5000

# Run the app
CMD ["python", "run.py"]
