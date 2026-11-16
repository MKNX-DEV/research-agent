FROM ghcr.io/astral-sh/uv:bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_INSTALL_DIR=/python
ENV UV_PYTHON_PREFERENCE=only-managed

WORKDIR /app

# Copy monorepo packages
COPY shared_libs ./shared_libs
COPY services/research_tools ./services/research_tools

# Move into the application package
WORKDIR /app/services/research_tools

# Copy Python version file
COPY services/research_tools/.python-version .

# Install requested Python version
RUN uv python install $(cat .python-version)

# Create venv with the correct interpreter
RUN uv venv --python $(cat .python-version)

# Install dependencies + project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

# -----------------------------------------------------------------------------

FROM debian:bookworm-slim

# Create non-root user
RUN groupadd --system --gid 999 nonroot \
 && useradd --system --gid 999 --uid 999 --create-home nonroot

# Copy Python runtime
COPY --from=builder /python /python

# Copy application
COPY --from=builder --chown=nonroot:nonroot /app /app

# Activate Python + venv
ENV PATH="/python/bin:/app/services/research_tools/.venv/bin:$PATH"

USER nonroot

# Match local monorepo structure
WORKDIR /app/services/research_tools

EXPOSE 8001

# Run application
CMD ["python", "-m", "research_tools.main"]