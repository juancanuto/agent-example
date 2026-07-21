FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agents ./agents

ENV PORT=8080
EXPOSE 8080

# api_server expõe REST; use `adk web` se preferir a Dev UI no container
CMD ["sh", "-c", "adk api_server --host 0.0.0.0 --port ${PORT} agents"]
