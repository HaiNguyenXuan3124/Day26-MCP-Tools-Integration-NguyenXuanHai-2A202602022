# Weather MCP Server — Streamable HTTP, deploy được lên Cloud Run
FROM python:3.12-slim

WORKDIR /app

# Cài dependencies trước để tận dụng layer cache
COPY pyproject.toml ./
RUN pip install --no-cache-dir . && rm -rf /root/.cache

# Copy code
COPY weather.py ./

# Cloud Run sẽ set PORT (thường 8080); local mặc định 8085
ENV PYTHONUNBUFFERED=1
EXPOSE 8080

# WEATHERAPI_KEY truyền qua biến môi trường lúc chạy (KHÔNG bake vào image)
CMD ["python", "weather.py"]
