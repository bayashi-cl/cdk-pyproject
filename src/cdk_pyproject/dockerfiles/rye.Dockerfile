# syntax=docker/dockerfile:1
ARG IMAGE

# hadolint ignore=DL3006
FROM ${IMAGE}

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
WORKDIR /workspace

ENV RYE_HOME="/opt/rye"
ENV PATH="${RYE_HOME}/shims:${PATH}"
RUN curl -sSf https://rye.astral.sh/get | RYE_NO_AUTO_INSTALL=1 RYE_INSTALL_OPTION="--yes" bash

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.lock,target=requirements.lock \
    pip wheel --wheel-dir /tmp/wheelhouse  --requirement <(sed '/^-e/d' requirements.lock)

COPY . .
RUN rye build --wheel --all --out /tmp/wheelhouse
