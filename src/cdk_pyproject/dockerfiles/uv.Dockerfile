# syntax=docker/dockerfile:1
ARG IMAGE
ARG PACKAGE

# hadolint ignore=DL3006
FROM ${IMAGE}

ARG PACKAGE=${PACKAGE}
SHELL ["/bin/bash", "-eo", "pipefail", "-c"]
WORKDIR /workspace

COPY . .
RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    uv pip install ${PACKAGE} --target /asset --constraints <(uv export --no-hashes --no-emit-workspace --frozen)
