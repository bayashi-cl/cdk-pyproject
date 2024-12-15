from pathlib import Path

import pytest
from aws_cdk import aws_lambda

from cdk_pyproject import PyProject


def test_pyproject(capsys: pytest.CaptureFixture[str]) -> None:
    project = PyProject.from_pyproject(str(Path(__file__).with_name("testproject")))
    assert project.runtime.runtime_equals(aws_lambda.Runtime.PYTHON_3_11)

    project.code(cache_disabled=True)
    captured = capsys.readouterr()
    assert "Installed 2 packages" in captured.err


def test_rye(capsys: pytest.CaptureFixture[str]) -> None:
    project = PyProject.from_rye(str(Path(__file__).with_name("testproject-rye")))
    assert project.runtime.runtime_equals(aws_lambda.Runtime.PYTHON_3_12)

    project.code("app/lambda-1", cache_disabled=True)
    captured = capsys.readouterr()
    assert "Installed 1 package" in captured.err

    project.code("app/lambda-2", cache_disabled=True)
    captured = capsys.readouterr()
    assert "Installed 3 packages" in captured.err


def test_uv(capsys: pytest.CaptureFixture[str]) -> None:
    project = PyProject.from_uv(str(Path(__file__).with_name("testproject-uv")))
    assert project.runtime.runtime_equals(aws_lambda.Runtime.PYTHON_3_12)

    project.code("app/uv-lambda-1", cache_disabled=True)
    captured = capsys.readouterr()
    assert "Installed 1 package" in captured.err

    project.code("app/uv-lambda-2", cache_disabled=True)
    captured = capsys.readouterr()
    assert "Installed 3 packages" in captured.err


def test_script(capsys: pytest.CaptureFixture[str]) -> None:
    script = PyProject.from_script(str(Path(__file__).with_name("script.py")))
    assert script.runtime.runtime_equals(aws_lambda.Runtime.PYTHON_3_11)

    script.code(cache_disabled=True)
    captured = capsys.readouterr()
    assert "Installed 6 packages" in captured.err
