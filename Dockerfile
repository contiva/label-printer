FROM python:3.11-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends fonts-dejavu-core \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV LABEL_PRINTER_DATA_DIR=/data \
    LABEL_PRINTER_HOST=0.0.0.0 \
    LABEL_PRINTER_PORT=3333

EXPOSE 3333

CMD ["python", "app.py"]
