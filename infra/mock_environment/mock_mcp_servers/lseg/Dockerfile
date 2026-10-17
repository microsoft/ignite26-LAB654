# Build from infra/mock_environment/mock_mcp_servers:
#   docker build -f lseg/Dockerfile -t mock-lseg:latest .
# On networks that block PyPI, add: --build-arg PIP_INDEX_URL=<your mirror>/simple/
FROM python:3.12-slim

ARG PIP_INDEX_URL=https://pypi.org/simple/
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/_framework:/app/_domains/finance:/app/lseg \
    MCP_TRANSPORT=http \
    PORT=8000

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --index-url "$PIP_INDEX_URL" -r requirements.txt

COPY _framework/ _framework/
COPY _domains/finance/ _domains/finance/
COPY lseg/ lseg/

RUN useradd --uid 10001 --no-create-home mcp
USER mcp

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import os,urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ.get(\"PORT\",\"8000\")}/healthz')"
CMD ["python", "-m", "mock_lseg"]
