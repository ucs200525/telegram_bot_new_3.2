FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the rest of the Node.js application code to the working directory
COPY . .

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy Python requirements and install
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy all other application files
COPY . /app/

# Expose the port the app runs on
EXPOSE 8080

# Run Python application
CMD ["python", "bot.py"]
