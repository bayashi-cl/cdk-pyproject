# syntax=docker/dockerfile:1
ARG IMAGE

# hadolint ignore=DL3006
FROM ${IMAGE}

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
WORKDIR /workspace

ENV RYE_HOME="/opt/rye"
ENV PATH="${RYE_HOME}/shims:${PATH}"
RUN curl -sSf https://rye.astral.sh/get | RYE_NO_AUTO_INSTALL=1 RYE_INSTALL_OPTION="--yes" bash
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY . .
RUN rye build --wheel --all --out /opt/wheelhouse && \
    sed '/^-e/d' requirements.lock > /opt/constraints.txt && \
    uv pip install . --system --find-links /opt/wheelhouse --constraints /opt/constraints.txt
