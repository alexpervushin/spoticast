FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/data

RUN useradd -m appuser
RUN chown -R appuser:appuser /app
RUN chown -R appuser:appuser /app/data

USER appuser

COPY --chown=appuser:appuser . .

VOLUME ["/app/data"]

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD curl -f http://localhost:8000/health || exit 1

ENV PYTHONPATH=/app

CMD ["python", "main.py"]