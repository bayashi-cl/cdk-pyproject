import importlib.resources
import os.path
from pathlib import Path
from typing import Self

import tomllib
from aws_cdk import BundlingOptions, DockerImage, aws_lambda
from pyproject_metadata import StandardMetadata

dockerfiles = importlib.resources.files("cdk_pyproject.dockerfiles")


class PyProject:
    def __init__(self, path: str, runtime: aws_lambda.Runtime, image: DockerImage) -> None:
        self.runtime = runtime
        self.image = image
        self.path = path

    @classmethod
    def from_pyproject(cls, path: str, runtime: aws_lambda.Runtime) -> Self:
        image = DockerImage.from_build(
            path=path,
            build_args={"IMAGE": runtime.bundling_image.image},
            file=os.path.relpath(str(dockerfiles.joinpath("pyproject.Dockerfile")), start=path),
        )

        return cls(path, runtime, image)

    @classmethod
    def from_rye(cls, path: str, runtime: aws_lambda.Runtime) -> Self:
        image = DockerImage.from_build(
            path=path,
            build_args={"IMAGE": runtime.bundling_image.image},
            file=os.path.relpath(str(dockerfiles.joinpath("rye.Dockerfile")), start=path),
        )

        return cls(path, runtime, image)

    @classmethod
    def from_poetry(cls, path: str, runtime: aws_lambda.Runtime) -> Self:
        raise NotImplementedError

    def get_root_project_name(self) -> str:
        pyproject = Path(self.path, "pyproject.toml")
        metadata = StandardMetadata.from_pyproject(tomllib.loads(pyproject.read_text()))
        return metadata.name

    def code(self, project: str | None = None) -> aws_lambda.Code:
        if project is None:
            project = self.get_root_project_name()

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
