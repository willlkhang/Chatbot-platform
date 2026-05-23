FROM nvidia/cuda:11.0.3-cudnn8-devel-ubuntu20.04 AS wheel-builder

ENV DEBIAN_FRONTEND=noninteractive

RUN rm -f /etc/apt/sources.list.d/cuda.list /etc/apt/sources.list.d/nvidia-ml.list

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl cmake make gcc g++ \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.11.16 /uv /uvx /bin/

ENV UV_PYTHON_INSTALL_DIR=/opt/uv-python \
    UV_LINK_MODE=copy

RUN uv python install 3.10

ENV CMAKE_ARGS="-DGGML_CUDA=on -DCMAKE_CUDA_ARCHITECTURES=75" \
    FORCE_CMAKE=1

RUN uv venv --seed --python 3.10 /opt/build-venv \
    && /opt/build-venv/bin/python -m pip wheel \
        --no-deps --no-cache-dir \
        "llama-cpp-python>=0.3.0" \
        -w /tmp/wheels


FROM nvidia/cuda:11.0.3-runtime-ubuntu20.04

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app


RUN rm -f /etc/apt/sources.list.d/cuda.list /etc/apt/sources.list.d/nvidia-ml.list

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.11.16 /uv /uvx /bin/
ENV UV_PYTHON_INSTALL_DIR=/opt/uv-python \
    UV_LINK_MODE=copy
RUN uv python install 3.10

COPY pyproject.toml uv.lock ./

RUN uv venv --python 3.10 /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

RUN uv sync --no-dev

COPY --from=wheel-builder /tmp/wheels/llama_cpp_python*.whl /tmp/
RUN uv pip install --force-reinstall /tmp/llama_cpp_python*.whl \
    && rm /tmp/llama_cpp_python*.whl

COPY . .

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