# syntax=docker/dockerfile:1
ARG IMAGE
ARG PACKAGE

# hadolint ignore=DL3006
FROM ${IMAGE}

ARG PACKAGE=${PACKAGE}
SHELL ["/bin/bash", "-eo", "pipefail", "-c"]
WORKDIR /workspace

RUN pip install --no-cache-dir pyproject-metadata==0.8.0

COPY ${PACKAGE} .
RUN cat <<EOF > compile.py
import re
import sys
import tomllib
from pathlib import Path

from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from pyproject_metadata import StandardMetadata


def read_script(path: Path) -> StandardMetadata:
    script = path.read_text()
    pat = re.compile(r"(?m)^# /// (?P<type>[a-zA-Z0-9-]+)$\s(?P<content>(^#(| .*)$\s)+)^# ///$")
    matches = list(filter(lambda m: m.group("type") == "script", pat.finditer(script)))
    if len(matches) > 1:
        msg = "invalid script inline metadata"
        raise ValueError(msg)
    if len(matches) == 1:
        content = "".join(
            line[2:] if line.startswith("# ") else line[1:]
            for line in matches[0].group("content").splitlines(keepends=True)
        )
        metadata = tomllib.loads(content)
        return StandardMetadata(
            name=path.name,
            requires_python=SpecifierSet(r) if (r := metadata.get("requires-python")) is not None else None,
            dependencies=[Requirement(r) for r in metadata.get("dependencies", [])],
        )
    return StandardMetadata(name=path.stem)


def main() -> None:
    metadata = read_script(Path(sys.argv[1]))
    requirements = "\n".join(map(str, metadata.dependencies))
    sys.stdout.write(requirements)


if __name__ == "__main__":
    main()
EOF

# hadolint ignore=DL3059
RUN python3 compile.py ${PACKAGE} > requirements.txt
RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    uv pip install -r ./requirements.txt --target /asset
RUN cp ${PACKAGE} /asset
