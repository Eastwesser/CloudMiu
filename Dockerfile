FROM python:3.10-slim

WORKDIR /app

# Только самое необходимое для компиляции aiohttp и psutil
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]

#FROM python:3.10-slim
#
#WORKDIR /app
#
#COPY . /app
#
#RUN pip install --no-cache-dir -r requirements.txt
#
#CMD ["python", "main.py"]
