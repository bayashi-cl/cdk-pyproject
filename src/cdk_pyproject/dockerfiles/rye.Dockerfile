# syntax=docker/dockerfile:1
ARG IMAGE
ARG PACKAGE

# hadolint ignore=DL3006
FROM ${IMAGE}

ARG PACKAGE=${PACKAGE}
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
WORKDIR /workspace

ENV RYE_HOME="/opt/rye"
ENV PATH="${RYE_HOME}/shims:${PATH}"
RUN curl -sSf https://rye.astral.sh/get | RYE_NO_AUTO_INSTALL=1 RYE_INSTALL_OPTION="--yes" bash

COPY . .
RUN rye build --wheel --all
RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    uv pip install ${PACKAGE} --find-links dist --target /asset --constraints <(sed '/^-e/d' requirements.lock)
