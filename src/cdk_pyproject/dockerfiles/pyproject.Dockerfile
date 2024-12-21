# syntax=docker/dockerfile:1
ARG IMAGE

# hadolint ignore=DL3006
FROM ${IMAGE}

SHELL ["/bin/bash", "-eo", "pipefail", "-c"]
WORKDIR /workspace

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY . .
RUN mkdir -p /opt/wheelhouse && \
    touch /opt/constraints.txt && if test -e constraints.txt; then cp constraints.txt /opt/constraints.txt; fi && \
    uv pip install . --system --find-links /opt/wheelhouse --constraints /opt/constraints.txt
