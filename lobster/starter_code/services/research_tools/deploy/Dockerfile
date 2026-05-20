FROM python:3.12-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the common library
COPY ../libs/common /app/common

# Copy the service code
COPY . .

# Expose port
EXPOSE 8001

# Run the application
CMD ["python", "main.py"]