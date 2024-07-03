import json
import os
import subprocess
from pathlib import Path
from typing import TypedDict

import nox

PYTHON_VERSIONS = ["3.11", "3.12"]
nox.options.default_venv_backend = "uv"


class ToolchainInfo(TypedDict):
    name: str
    path: str


def ensure_python() -> None:
    for version in PYTHON_VERSIONS:
        subprocess.check_call(["rye", "toolchain", "fetch", version])  # noqa:  S603, S607

    output = subprocess.check_output(["rye", "toolchain", "list", "--format", "json"], text=True)  # noqa:  S603, S607
    toolchain_list: list[ToolchainInfo] = json.loads(output)
    paths = env_path.split(":") if (env_path := os.getenv("PATH")) is not None else []
    python_paths = [str(Path(toolchain["path"]).parent) for toolchain in toolchain_list]

    os.environ["PATH"] = ":".join(python_paths + paths)


ensure_python()


@nox.session(python=PYTHON_VERSIONS)
def tests(session: nox.Session) -> None:
    session.install("-r", "requirements-dev.lock")
    session.run("pytest")
    session.run("mypy", ".")


@nox.session()
def lint(session: nox.Session) -> None:
    session.install("-r", "requirements-dev.lock")
    session.run("ruff", "check")
