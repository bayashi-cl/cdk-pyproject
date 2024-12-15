import importlib.resources
import os.path
from pathlib import Path
from typing import Self

from aws_cdk import aws_lambda as lambda_

import cdk_pyproject.dockerfiles
from cdk_pyproject.utils import (
    read_pyproject,
    read_script,
    runtime_from_metadata,
    runtime_from_python_version,
    runtime_from_sys,
)

_dockerfiles = importlib.resources.files(cdk_pyproject.dockerfiles)


class PyProject:
    def __init__(self, path: str, runtime: lambda_.Runtime, dockerfile: str, *, package: str | None = None) -> None:
        self.path = path
        self.runtime = runtime
        self.dockerfile = dockerfile
        self.package = package

    @classmethod
    def from_pyproject(cls, path: str, runtime: lambda_.Runtime | None = None) -> Self:
        if runtime is None:
            metadata = read_pyproject(Path(path))
            runtime = runtime_from_python_version(path) or runtime_from_metadata(metadata) or runtime_from_sys()

        return cls(path=path, runtime=runtime, dockerfile="pyproject.Dockerfile")

    @classmethod
    def from_script(cls, path: str, runtime: lambda_.Runtime | None = None) -> Self:
        path_obj = Path(path)
        if runtime is None:
            metadata = read_script(path_obj)
            runtime = runtime_from_metadata(metadata) or runtime_from_sys()

        return cls(path=str(path_obj.parent), runtime=runtime, dockerfile="script.Dockerfile", package=path_obj.name)

    @classmethod
    def from_rye(cls, path: str, runtime: lambda_.Runtime | None = None) -> Self:
        if runtime is None:
            metadata = read_pyproject(Path(path))
            runtime = runtime_from_python_version(path) or runtime_from_metadata(metadata) or runtime_from_sys()
        return cls(path=path, runtime=runtime, dockerfile="rye.Dockerfile")

    @classmethod
    def from_poetry(cls, path: str, runtime: lambda_.Runtime | None = None) -> Self:
        if runtime is None:
            metadata = read_pyproject(Path(path))
            runtime = runtime_from_metadata(metadata) or runtime_from_sys()
        raise NotImplementedError
        return cls(path=path, runtime=runtime, dockerfile="code-uv.Dockerfile")

    @classmethod
    def from_uv(cls, path: str, runtime: lambda_.Runtime | None = None) -> Self:
        if runtime is None:
            metadata = read_pyproject(Path(path))
            runtime = runtime_from_python_version(path) or runtime_from_metadata(metadata) or runtime_from_sys()
        return cls(path=path, runtime=runtime, dockerfile="uv.Dockerfile")

    def code(self, package: str | None = None, *, cache_disabled: bool | None = None) -> lambda_.Code:
        self.package = package or self.package or "."

        return lambda_.Code.from_docker_build(
            self.path,
            file=os.path.relpath(str(_dockerfiles.joinpath(self.dockerfile)), start=self.path),
            build_args={"IMAGE": self.runtime.bundling_image.image, "PACKAGE": self.package},
            cache_disabled=cache_disabled,
        )
