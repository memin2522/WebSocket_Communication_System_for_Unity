FROM python:3.12-slim
WORKDIR /app
ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY wsgi.py .
EXPOSE 5000
CMD ["sh", "-c", "gunicorn -k eventlet -w 1 -b 0.0.0.0:${PORT} wsgi:app"]
