import contextlib
import os
import subprocess
from pathlib import Path

import nox


def find_python(python: list[str]) -> None:
    paths = []
    for py in python:
        with contextlib.suppress(subprocess.CalledProcessError):
            d = subprocess.check_output(["uv", "python", "find", py], text=True).strip()  # noqa: S603, S607
            paths.append(str(Path(d).parent))

    orig_paths = os.environ["PATH"].split(os.pathsep)
    os.environ["PATH"] = os.pathsep.join(paths + orig_paths)


nox.options.default_venv_backend = "uv"
find_python(["3.11", "3.12"])


@nox.session(python=["3.11", "3.12"])
def test(session: nox.Session) -> None:
    session.install("--upgrade", ".", "pytest")
    session.run("pytest")


@nox.session
def type_check(session: nox.Session) -> None:
    session.install("--upgrade", ".", "mypy", "pytest", "nox")
    session.run("mypy", ".")


@nox.session
def lint(session: nox.Session) -> None:
    session.install("--upgrade", ".", "ruff")
    session.run("ruff", "check", ".")
