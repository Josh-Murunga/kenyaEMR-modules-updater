# Use an official Python image and install Java 8
FROM python:3.11-slim

# Install Java 8 and other dependencies
RUN apt-get update && \
    apt-get install -y openjdk-8-jdk wget git maven && \
    rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

# Set work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your script and any other needed files
COPY update_modules.py .
COPY modules.xlsx .

# Entrypoint
# CMD ["python", "update_modules.py"]