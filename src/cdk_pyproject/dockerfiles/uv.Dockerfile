# syntax=docker/dockerfile:1
ARG IMAGE

# hadolint ignore=DL3006
FROM ${IMAGE}

SHELL ["/bin/bash", "-eo", "pipefail", "-c"]
WORKDIR /workspace

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=uv.lock,target=/workspace/uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    pip wheel --wheel-dir /tmp/wheelhouse  --requirement <(uv export --no-hashes --no-emit-workspace --frozen)

COPY . .
RUN uv build --wheel --all --out-dir /tmp/wheelhouse
