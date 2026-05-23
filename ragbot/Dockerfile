# CUDA 11.0 devel image — matches the GRID T4-16Q vGPU driver (450.x / CUDA 11.0).
# We need the *devel* variant at build time so cmake can find cublas headers.
FROM nvidia/cuda:11.0.3-cudnn8-devel-ubuntu20.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Python 3.12 via deadsnakes PPA (Ubuntu 20.04 ships 3.8 only).
RUN apt-get update && apt-get install -y --no-install-recommends \
        software-properties-common curl gnupg2 ca-certificates \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y --no-install-recommends \
        python3.12 python3.12-dev python3.12-venv \
        cmake make gcc g++ \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1 \
    && update-alternatives --install /usr/bin/python  python  /usr/bin/python3.12 1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.6.14 /uv /uvx /bin/

COPY pyproject.toml uv.lock ./

# Build llama-cpp-python with cuBLAS.
# sm_75 = Turing (T4). GGML_CUDA replaces the old LLAMA_CUBLAS flag in >=0.3.
ENV CMAKE_ARGS="-DGGML_CUDA=on -DCMAKE_CUDA_ARCHITECTURES=75" \
    FORCE_CMAKE=1

# uv sync resolves + installs; compile llama-cpp-python from source using the
# CMAKE_ARGS above.  Drop --frozen so a regenerated lock is not required.
RUN uv sync --no-dev

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
