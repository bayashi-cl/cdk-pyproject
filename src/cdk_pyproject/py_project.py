import importlib.resources
import os.path
from pathlib import Path
from typing import Self

from aws_cdk import BundlingOptions, DockerImage, aws_lambda
from pyproject_metadata import StandardMetadata

from cdk_pyproject.utils import read_pyproject, runtime_from_metadata, runtime_from_sys

_dockerfiles = importlib.resources.files("cdk_pyproject.dockerfiles")


class PyProject:
    def __init__(self, path: str, runtime: aws_lambda.Runtime, image: DockerImage, metadata: StandardMetadata) -> None:
        self.runtime = runtime
        self.image = image
        self.path = path
        self.metadata = metadata

    @classmethod
    def from_pyproject(cls, path: str, runtime: aws_lambda.Runtime | None = None) -> Self:
        metadata = read_pyproject(Path(path))
        if runtime is None:
            runtime = runtime_from_metadata(metadata) or runtime_from_sys()
        image = DockerImage.from_build(
            path=path,
            build_args={"IMAGE": runtime.bundling_image.image},
            file=os.path.relpath(str(_dockerfiles.joinpath("pyproject.Dockerfile")), start=path),
        )

        return cls(path, runtime, image, metadata)

    @classmethod
    def from_rye(cls, path: str, runtime: aws_lambda.Runtime | None = None) -> Self:
        metadata = read_pyproject(Path(path))
        if runtime is None:
            runtime = runtime_from_metadata(metadata) or runtime_from_sys()
        image = DockerImage.from_build(
            path=path,
            build_args={"IMAGE": runtime.bundling_image.image},
            file=os.path.relpath(str(_dockerfiles.joinpath("rye.Dockerfile")), start=path),
        )

        return cls(path, runtime, image, metadata)

    @classmethod
    def from_poetry(cls, path: str, runtime: aws_lambda.Runtime) -> Self:
        raise NotImplementedError

    @classmethod
    def from_uv(cls, path: str, runtime: aws_lambda.Runtime | None = None) -> Self:
        metadata = read_pyproject(Path(path))
        if runtime is None:
            runtime = runtime_from_metadata(metadata) or runtime_from_sys()
        image = DockerImage.from_build(
            path=path,
            build_args={"IMAGE": runtime.bundling_image.image},
            file=os.path.relpath(str(_dockerfiles.joinpath("uv.Dockerfile")), start=path),
        )

        return cls(path, runtime, image, metadata)

    def code(self, project: str | None = None) -> aws_lambda.Code:
        if project is None:
            project = self.metadata.name

        return aws_lambda.Code.from_asset(
            path=".",
            bundling=BundlingOptions(
                image=self.image,
                command=[
                    "bash",
                    "-eux",
                    "-c",
                    f"pip install --find-links /tmp/wheelhouse --no-index --target /asset-output {project}",
                ],
                user="root",
            ),
        )
