# Raspberry Pi 3B+ (armv7l):
#   docker buildx build --platform linux/arm/v7 -t eastwesser/home_arm_miumiu2:latest --push .
# Windows/x86 local smoke (not for the Pi):
#   docker compose build
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

# polling by default; override via compose/.env
CMD ["python", "main.py"]
