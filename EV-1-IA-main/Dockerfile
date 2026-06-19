# Build with:  docker build -t unimarc-app .
# Run with:    docker run -p 8501:8501 --env-file .env unimarc-app

FROM python:3-slim

RUN useradd --create-home appuser

WORKDIR /app

COPY --chown=appuser:appuser . .

RUN pip install --no-cache-dir -r requirements.txt

USER appuser

EXPOSE 8501

CMD ["streamlit", "run", "main.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
