# syntax=docker/dockerfile:1
ARG IMAGE

# hadolint ignore=DL3006
FROM ${IMAGE}

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
WORKDIR /workspace

RUN pip install --no-cache-dir build==1.2.1 uv==0.2.21

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    pip wheel --wheel-dir /tmp/wheelhouse  --requirement <(uv pip compile pyproject.toml)

COPY . .
RUN pyproject-build --wheel --outdir /tmp/wheelhouse
