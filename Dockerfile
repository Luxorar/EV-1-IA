# Build with:  docker build -t my-app .
# Run with:    docker run -p 8080:8080 my-app

FROM python:3-slim

WORKDIR /app

# Install dependencies first so this layer is cached
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["streamlit", "run", "main.py", "--server.port", "8080", "--server.address", "0.0.0.0"]
