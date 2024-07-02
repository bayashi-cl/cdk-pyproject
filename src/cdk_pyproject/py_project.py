import importlib.resources
import os.path
import sys
import tomllib
from pathlib import Path
from typing import Self

from aws_cdk import BundlingOptions, DockerImage, aws_lambda
from pyproject_metadata import StandardMetadata

dockerfiles = importlib.resources.files("cdk_pyproject.dockerfiles")


def runtime_from_sys() -> aws_lambda.Runtime:
    if sys.version_info.major != 3:  # noqa: PLR2004
        msg = "system python is not python3"
        raise ValueError(msg)

    result: aws_lambda.Runtime
    match sys.version_info.minor:
        case 8:
            result = aws_lambda.Runtime.PYTHON_3_8
        case 9:
            result = aws_lambda.Runtime.PYTHON_3_9
        case 10:
            result = aws_lambda.Runtime.PYTHON_3_10
        case 11:
            result = aws_lambda.Runtime.PYTHON_3_11
        case 12:
            result = aws_lambda.Runtime.PYTHON_3_12
        case _:
            msg = "unsupported python minor version"
            raise ValueError(msg)
    return result


class PyProject:
    def __init__(self, path: str, runtime: aws_lambda.Runtime, image: DockerImage) -> None:
        self.runtime = runtime
        self.image = image
        self.path = path

    @classmethod
    def from_pyproject(cls, path: str, runtime: aws_lambda.Runtime | None = None) -> Self:
        if runtime is None:
            runtime = runtime_from_sys()
        image = DockerImage.from_build(
            path=path,
            build_args={"IMAGE": runtime.bundling_image.image},
            file=os.path.relpath(str(dockerfiles.joinpath("pyproject.Dockerfile")), start=path),
        )

        return cls(path, runtime, image)

    @classmethod
    def from_rye(cls, path: str, runtime: aws_lambda.Runtime | None = None) -> Self:
        if runtime is None:
            runtime = runtime_from_sys()
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
