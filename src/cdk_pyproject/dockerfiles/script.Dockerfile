# syntax=docker/dockerfile:1
ARG IMAGE

# hadolint ignore=DL3006
FROM ${IMAGE}

ARG SCRIPT
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
WORKDIR /workspace

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    pip wheel --wheel-dir /tmp/wheelhouse  --requirement requirements.txt

COPY ${SCRIPT} /tmp/
