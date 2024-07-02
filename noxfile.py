import os
from pathlib import Path

import nox

PYTHON_VERSIONS = ["3.11", "3.12"]
VENV_BACKEND = "uv"


def ensurepath() -> None:
    rye_home = os.getenv("RYE_HOME")
    rye_py = Path(rye_home) if rye_home else Path.home() / ".rye" / "py"

    for py_dir in rye_py.iterdir():
        bin_dir = py_dir / "bin"
        os.environ["PATH"] = f"{bin_dir}:{os.environ['PATH']}"


ensurepath()


@nox.session()
def fetch(session: nox.Session) -> None:
    for require_version in PYTHON_VERSIONS:
        session.run("rye", "fetch", require_version, external=True)

    ensurepath()


@nox.session(python=PYTHON_VERSIONS, venv_backend=VENV_BACKEND)
def tests(session: nox.Session) -> None:
    session.install("-r", "requirements-dev.lock")
    session.run("pytest")
    session.run("mypy", ".")


@nox.session(venv_backend=VENV_BACKEND)
def lint(session: nox.Session) -> None:
    session.install("-r", "requirements-dev.lock")
    session.run("ruff", "check")
