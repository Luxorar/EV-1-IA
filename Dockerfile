# Build with:  docker build -t unimarc-app .
# Run with:    docker run -p 8080:8080 --env-file .env unimarc-app

FROM python:3-slim

RUN useradd --create-home appuser

WORKDIR /app

COPY --chown=appuser:appuser . .

RUN pip install --no-cache-dir -r requirements.txt

USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import http.client; c=http.client.HTTPConnection('localhost:8080'); c.request('GET','/'); r=c.getresponse(); exit(0 if r.status==200 else 1)"

CMD ["streamlit", "run", "main.py", "--server.port", "8080", "--server.address", "0.0.0.0"]
