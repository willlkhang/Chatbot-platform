# =============================================================
# Stage 1 — compile llama-cpp-python with CUDA 11.0 / cuBLAS
#   Base: nvidia/cuda 11.0 devel (Ubuntu 20.04)
#   Python 3.12 via deadsnakes — added manually to avoid
#   add-apt-repository misbehaving inside Docker.
# =============================================================
FROM nvidia/cuda:11.0.3-cudnn8-devel-ubuntu20.04 AS wheel-builder

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        gnupg2 ca-certificates curl cmake make gcc g++ \
    && curl -fsSL \
        "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0xF23C5A6CF475977595C89F51BA6932366A755776" \
        | gpg --dearmor -o /etc/apt/trusted.gpg.d/deadsnakes.gpg \
    && echo "deb http://ppa.launchpad.net/deadsnakes/ppa/ubuntu focal main" \
        > /etc/apt/sources.list.d/deadsnakes.list \
    && apt-get update && apt-get install -y --no-install-recommends \
        python3.12 python3.12-dev python3.12-distutils \
    && curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12 \
    && rm -rf /var/lib/apt/lists/*

# sm_75 = Turing (T4).  GGML_CUDA replaces the old LLAMA_CUBLAS flag in >=0.3.
ENV CMAKE_ARGS="-DGGML_CUDA=on -DCMAKE_CUDA_ARCHITECTURES=75" \
    FORCE_CMAKE=1

RUN python3.12 -m pip wheel --no-deps --no-cache-dir \
        "llama-cpp-python>=0.3.0" -w /tmp/wheels


# =============================================================
# Stage 2 — runtime
#   Base: official python:3.12-slim-bookworm (has Python headers
#   built-in, so no -dev package needed).
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
