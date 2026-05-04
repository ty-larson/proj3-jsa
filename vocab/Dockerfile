# Use a lightweight Python base image
FROM python:3.8-slim

# Set the working directory for the application
WORKDIR /app

# Install dependencies from the requirements file
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files into the container
COPY . .

# Start the Flask application
CMD ["python", "flask_vocab.py"]