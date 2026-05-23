# =============================================================
# Stage 1 — compile llama-cpp-python with CUDA 11.0 / cuBLAS
#   Base: nvidia/cuda 11.0 devel (Ubuntu 20.04)
#   Python 3.12: provided by `uv python install` (portable build),
#   so we don't need the deadsnakes PPA or any system python3.12.
# =============================================================
FROM nvidia/cuda:11.0.3-cudnn8-devel-ubuntu20.04 AS wheel-builder

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl cmake make gcc g++ \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.6.14 /uv /uvx /bin/

ENV UV_PYTHON_INSTALL_DIR=/opt/uv-python \
    UV_LINK_MODE=copy

RUN uv python install 3.12

# sm_75 = Turing (T4). GGML_CUDA replaces the old LLAMA_CUBLAS flag in >=0.3.
ENV CMAKE_ARGS="-DGGML_CUDA=on -DCMAKE_CUDA_ARCHITECTURES=75" \
    FORCE_CMAKE=1

# Create a Python 3.12 venv with pip seeded, then build the wheel.
RUN uv venv --seed --python 3.12 /opt/build-venv \
    && /opt/build-venv/bin/python -m pip wheel \
        --no-deps --no-cache-dir \
        "llama-cpp-python>=0.3.0" \
        -w /tmp/wheels


# =============================================================
# Stage 2 — runtime
#   Base: official python:3.12-slim-bookworm.
# =============================================================
FROM python:3.12-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.6.14 /uv /uvx /bin/

COPY pyproject.toml uv.lock ./

# Install all runtime deps (this pulls a CPU llama-cpp-python from PyPI).
RUN uv sync --no-dev

# Replace the CPU wheel with the CUDA-enabled one built in Stage 1.
COPY --from=wheel-builder /tmp/wheels/llama_cpp_python*.whl /tmp/
RUN uv pip install --force-reinstall /tmp/llama_cpp_python*.whl \
    && rm /tmp/llama_cpp_python*.whl

COPY . .

# Seed runtime SQLite DBs from baked-in copies on first start.
RUN mkdir -p /opt/ragbot-seed \
    && cp /app/data/*.sqlite /opt/ragbot-seed/ 2>/dev/null || true \
    && chmod +x /app/docker-entrypoint.sh

ENV RAGBOT_HOST=0.0.0.0 \
    RAGBOT_PORT=5000 \
    RAGBOT_THREADS=16 \
    RAGBOT_DEBUG=false \
    RAGBOT_LOG_LEVEL=INFO \
    LLAMA_N_GPU_LAYERS=33 \
    HF_HOME=/app/hf_cache

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD curl -fsS http://127.0.0.1:5000/healthz || exit 1

ENTRYPOINT ["/app/docker-entrypoint.sh"]
