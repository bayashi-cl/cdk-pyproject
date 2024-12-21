import importlib.resources
import os
import shutil
import tempfile
from pathlib import Path
from typing import Self

from aws_cdk import BundlingOptions, DockerImage, aws_lambda
from pyproject_metadata import StandardMetadata
from typing_extensions import deprecated

from cdk_pyproject.utils import read_script, runtime_from_metadata, runtime_from_sys

_dockerfiles = importlib.resources.files("cdk_pyproject.dockerfiles")


@deprecated("Use py_project")
class PyScript:
    def __init__(self, path: str, runtime: aws_lambda.Runtime, image: DockerImage, metadata: StandardMetadata) -> None:
        self.runtime = runtime
        self.image = image
        self.path = path
        self.metadata = metadata

    @classmethod
    def from_script(cls, path: str, runtime: aws_lambda.Runtime | None = None) -> Self:
        metadata = read_script(Path(path))

        if runtime is None:
            runtime = runtime_from_metadata(metadata) or runtime_from_sys()

        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copy(path, tmpdir)
            requirements = "\n".join(str(dep) for dep in metadata.dependencies)
            Path(tmpdir, "requirements.txt").write_text(requirements)

            image = DockerImage.from_build(
                path=tmpdir,
                build_args={
                    "IMAGE": runtime.bundling_image.image,
                    "SCRIPT": Path(path).name,
                },
                file=os.path.relpath(str(_dockerfiles.joinpath("script.Dockerfile")), start=tmpdir),
            )

        return cls(path, runtime, image, metadata)

    def code(self) -> aws_lambda.Code:
        return aws_lambda.Code.from_asset(
            path=".",
            bundling=BundlingOptions(
                image=self.image,
                command=[
                    "bash",
                    "-eux",
                    "-c",
                    (
                        "pip install --target /asset-output /tmp/wheelhouse/*.whl "
                        f"&& cp /tmp/{Path(self.path).name} /asset-output"
                    ),
                ],
            ),
        )
