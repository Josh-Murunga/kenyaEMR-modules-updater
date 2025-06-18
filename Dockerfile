FROM openjdk:8-jdk

# Install Python 3, pip, and other dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-pip git wget maven && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY update_modules.py .
COPY modules.xlsx .

# No CMD or ENTRYPOINT here, so nothing runs by default