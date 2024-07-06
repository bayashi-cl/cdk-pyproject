import pytest
from aws_cdk.aws_lambda import Runtime
from cdk_pyproject.utils import resolve_runtime
from packaging.specifiers import SpecifierSet


@pytest.mark.parametrize("spec", ["==3.11", "==3.11.*", ">=3.11.0,<3.12"])
def test_runtime_is_311(spec: str) -> None:
    runtime = resolve_runtime(SpecifierSet(spec))
    assert runtime.runtime_equals(Runtime.PYTHON_3_11)


@pytest.mark.parametrize("spec", ["==3.10", "==3.12", "~=3.11", ">=3.11.1"])
def test_runtime_is_not_311(spec: str) -> None:
    runtime = resolve_runtime(SpecifierSet(spec))
    assert not runtime.runtime_equals(Runtime.PYTHON_3_11)
