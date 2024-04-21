import importlib.resources
import os.path
import tempfile
from pathlib import Path
from typing import Self

from aws_cdk import BundlingOptions, DockerImage, aws_lambda

dockerfiles = importlib.resources.files("cdk_pyproject.dockerfiles")


class PyProject:
    def __init__(self, runtime: aws_lambda.Runtime, image: DockerImage) -> None:
        self.runtime = runtime
        self.image = image

    @classmethod
    def from_rye(cls, runtime: aws_lambda.Runtime, path: str) -> Self:
        image = DockerImage.from_build(
            path=path,
            build_args={"IMAGE": runtime.bundling_image.image},
            file=os.path.relpath(str(dockerfiles.joinpath("rye.Dockerfile")), start=path),
        )

        return cls(runtime=runtime, image=image)

    def code(self, project: str) -> aws_lambda.Code:
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
