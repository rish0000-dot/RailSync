# ============================================================
# RailSync 2.0 — Multi-Stage Docker Build
# Stage 1: Build React/Vite frontend
# Stage 2: FastAPI backend serves API + static frontend
# Hugging Face Spaces requires port 7860
# ============================================================

# ---- Stage 1: Frontend Build ----
FROM node:20-slim AS frontend-builder

WORKDIR /build/frontend

# Install deps
COPY Frontend/package.json Frontend/package-lock.json ./
RUN npm ci --prefer-offline

# Copy source and build
COPY Frontend/ ./
# In production: API calls go to same origin (relative URLs)
ENV VITE_API_URL=""
RUN npm run build

# ---- Stage 2: Python Backend + Static Serving ----
FROM python:3.11-slim

# System deps for psycopg2-binary and ortools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY Backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY Backend/ ./Backend/

# Copy ML model artifacts (Layer 0-3 CSV outputs — needed at runtime)
COPY Railsync_Layer1_Complete/ ./Railsync_Layer1_Complete/
COPY Railsync_Layer2_Outputs/ ./Railsync_Layer2_Outputs/
COPY Railsync_2.0_Layer_0_FINAL/ ./Railsync_2.0_Layer_0_FINAL/

# Copy built frontend static files
COPY --from=frontend-builder /build/frontend/dist ./frontend_dist/

# Create non-root user for security
RUN useradd -m -u 1000 railsync && chown -R railsync:railsync /app
USER railsync

# Hugging Face Spaces uses port 7860
EXPOSE 7860

# Environment defaults (override via HF Space Secrets)
ENV PORT=7860 \
    LOG_LEVEL=INFO \
    LAYER_MODE=standalone \
    CORS_ORIGINS="*" \
    PYTHONPATH="/app:/app/Backend"

# Run FastAPI with Uvicorn
CMD ["python", "-m", "uvicorn", "Backend.app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "7860", \
     "--workers", "1", \
     "--log-level", "info", \
     "--app-dir", "/app"]
