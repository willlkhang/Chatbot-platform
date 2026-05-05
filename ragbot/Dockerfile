FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
# Install uv (optional) + dependencies (pip is more tolerant of requirements formatting)
RUN pip install --no-cache-dir uv
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

ENV HOST=0.0.0.0 \
    PORT=5000

CMD ["python", "controller.py"]
