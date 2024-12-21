import importlib.resources
import os.path
import textwrap
from pathlib import Path
from typing import Self

from aws_cdk import BundlingOptions, DockerImage
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
    def __init__(
        self,
        path: str,
        runtime: lambda_.Runtime,
        image: DockerImage,
        *,
        cmd: str | None = None,
    ) -> None:
        self.path = path
        self.runtime = runtime
        self.image = image
        self.cmd = cmd

    @classmethod
    def from_pyproject(cls, path: str, runtime: lambda_.Runtime | None = None) -> Self:
        if runtime is None:
            metadata = read_pyproject(Path(path))
            runtime = runtime_from_python_version(path) or runtime_from_metadata(metadata) or runtime_from_sys()

        image = DockerImage.from_build(
            path=path,
            build_args={"IMAGE": runtime.bundling_image.image},
            file=os.path.relpath(str(_dockerfiles.joinpath("pyproject.Dockerfile")), start=path),
        )
        return cls(path=path, runtime=runtime, image=image)

    @classmethod
    def from_script(cls, path: str, runtime: lambda_.Runtime | None = None) -> Self:
        path_obj = Path(path)
        if runtime is None:
            metadata = read_script(path_obj)
            runtime = runtime_from_metadata(metadata) or runtime_from_sys()

        image = DockerImage.from_build(
            path=str(path_obj.parent),
            build_args={"IMAGE": runtime.bundling_image.image, "PACKAGE": path_obj.name},
            file=os.path.relpath(str(_dockerfiles.joinpath("script.Dockerfile")), start=path_obj.parent),
        )
        return cls(
            path=str(path_obj.parent),
            runtime=runtime,
            image=image,
            cmd=textwrap.dedent(
                f"""\
                uv pip install --target /asset-output --requirements /opt/requirements.txt
                cp {path_obj.name} /asset-output
                """,
            ),
        )

    @classmethod
    def from_rye(cls, path: str, runtime: lambda_.Runtime | None = None) -> Self:
        if runtime is None:
            metadata = read_pyproject(Path(path))
            runtime = runtime_from_python_version(path) or runtime_from_metadata(metadata) or runtime_from_sys()

        image = DockerImage.from_build(
            path=path,
            build_args={"IMAGE": runtime.bundling_image.image},
            file=os.path.relpath(str(_dockerfiles.joinpath("rye.Dockerfile")), start=path),
        )
        return cls(path=path, runtime=runtime, image=image)

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

        image = DockerImage.from_build(
            path=path,
            build_args={"IMAGE": runtime.bundling_image.image},
            file=os.path.relpath(str(_dockerfiles.joinpath("uv.Dockerfile")), start=path),
        )
        return cls(path=path, runtime=runtime, image=image)

    def code(self, package: str | None = None) -> lambda_.Code:
        if package is None:
            package = "."

        cmd = self.cmd or textwrap.dedent(
            f"""\
            uv pip install \\
            --find-links /opt/wheelhouse \\
            --constraints /opt/constraints.txt \\
            --target /asset-output {package}
            """,
        )

        return lambda_.Code.from_asset(
            path=self.path,
            bundling=BundlingOptions(
                image=self.image,
                command=["bash", "-eux", "-c", cmd],
                user="root",
            ),
        )
