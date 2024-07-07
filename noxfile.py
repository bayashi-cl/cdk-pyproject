import json
import os
import subprocess
from pathlib import Path
from typing import TypedDict

import nox

nox.options.default_venv_backend = "uv"


class ToolchainInfo(TypedDict):
    name: str
    path: str


def ensure_python() -> None:
    try:
        output = subprocess.check_output(["rye", "toolchain", "list", "--format", "json"], text=True)  # noqa:  S603, S607
    except FileNotFoundError:
        pass
    else:
        toolchain_list: list[ToolchainInfo] = json.loads(output)
        paths = env_path.split(":") if (env_path := os.getenv("PATH")) is not None else []
        python_paths = [str(Path(toolchain["path"]).parent) for toolchain in toolchain_list]

        os.environ["PATH"] = ":".join(python_paths + paths)


ensure_python()


@nox.session(python=["3.11", "3.12"])
def ci(session: nox.Session) -> None:
    session.install("-r", "requirements-dev.lock")
    session.run("pytest")
    session.run("mypy", ".")
    session.run("ruff", "check", ".")
