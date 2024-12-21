# syntax=docker/dockerfile:1
ARG IMAGE

# hadolint ignore=DL3006
FROM ${IMAGE}

SHELL ["/bin/bash", "-eo", "pipefail", "-c"]
WORKDIR /workspace

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY . .
RUN uv build --all-packages --wheel --out-dir /opt/wheelhouse && \
    uv export --no-hashes --no-emit-workspace --frozen --output-file /opt/constraints.txt && \
    uv pip install . --system --find-links /opt/wheelhouse --constraints /opt/constraints.txt
