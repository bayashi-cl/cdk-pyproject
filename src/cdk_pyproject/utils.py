import sys
import tomllib
from pathlib import Path

from aws_cdk import aws_lambda
from packaging.specifiers import Specifier, SpecifierSet
from packaging.version import Version
from pyproject_metadata import StandardMetadata


def read_pyproject(path: Path) -> StandardMetadata:
    pyproject = path / "pyproject.toml"
    return StandardMetadata.from_pyproject(
        data=tomllib.loads(pyproject.read_text()),
        project_dir=path,
    )


def resolve_runtime(spec: Specifier | SpecifierSet) -> aws_lambda.Runtime:
    versions: list[tuple[Version, aws_lambda.Runtime]] = []
    for runtime in aws_lambda.Runtime.ALL:
        assert isinstance(runtime, aws_lambda.Runtime)  # noqa: S101
        if runtime.family == aws_lambda.RuntimeFamily.PYTHON:
            name: str = runtime.name
            versions.append((Version(name.removeprefix("python")), runtime))
    versions.sort(reverse=True)

    for version, runtime in versions:
        if version in spec:
            return runtime  # type: ignore[no-any-return]

    msg = "runtime not found"
    raise ValueError(msg)


def runtime_from_sys() -> aws_lambda.Runtime:
    sys_version = sys.version_info
    return resolve_runtime(Specifier(f"=={sys_version.major}.{sys_version.minor}"))


def runtime_from_metadata(metadata: StandardMetadata) -> aws_lambda.Runtime | None:
    requires_python = metadata.requires_python
    if requires_python is None:
        return None
    return resolve_runtime(requires_python)
