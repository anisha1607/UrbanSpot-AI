# ── Stage 1: Build ─────────────────────────────────────────────────────────
FROM python:3.11-slim AS base

# System dependencies (for kaleido/plotly image export + fpdf2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (layer-cached)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Stage 2: App ────────────────────────────────────────────────────────────
# Copy source code (secrets are NOT included — .dockerignore excludes .env)
COPY . .

# Create data output directories so the app doesn't crash at runtime
RUN mkdir -p data/outputs data/raw

# Cloud Run requires the app to listen on PORT env var (default 8080)
ENV PORT=8080
EXPOSE 8080

# Streamlit config: headless mode, correct port for Cloud Run
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

CMD ["streamlit", "run", "app/streamlit_app.py", \
     "--server.port=8080", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
