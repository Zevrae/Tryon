# ==========================================
# Stage 1: Builder
# ==========================================
FROM python:3.12-slim AS builder

# Inject uv binaries directly from Astral's official distroless image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Enable bytecode compilation for faster app cold-starts
ENV UV_COMPILE_BYTECODE=1
# Force uv to copy files instead of hard-linking to avoid cross-filesystem cache issues
ENV UV_LINK_MODE=copy

# 1. Install dependencies FIRST (without the project code) to maximize Docker layer caching
# We mount uv.lock and pyproject.toml temporarily so they don't break the cache layer
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# 2. Copy the actual application folders and files (NOW INCLUDING .env)
COPY pyproject.toml uv.lock .env ./
COPY server.py ./
COPY api/ ./api/
COPY core/ ./core/
COPY schemas/ ./schemas/
COPY services/ ./services/
COPY utils/ ./utils/

# 3. Install the project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ==========================================
# Stage 2: Runtime
# ==========================================
FROM python:3.12-slim

# Create a non-root user to enhance container security
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copy the isolated virtual environment from the builder stage
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Prioritize the virtual environment executables in the system PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copy only the necessary runtime files from the builder (NOW INCLUDING .env)
COPY --from=builder --chown=appuser:appuser /app/.env ./.env
COPY --from=builder --chown=appuser:appuser /app/server.py ./server.py
COPY --from=builder --chown=appuser:appuser /app/api/ ./api/
COPY --from=builder --chown=appuser:appuser /app/core/ ./core/
COPY --from=builder --chown=appuser:appuser /app/schemas/ ./schemas/
COPY --from=builder --chown=appuser:appuser /app/services/ ./services/
COPY --from=builder --chown=appuser:appuser /app/utils/ ./utils/

# Run the container as the unprivileged user
USER appuser

# Expose the port FastAPI will run on
EXPOSE 8000

# Start the application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]