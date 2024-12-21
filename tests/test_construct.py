from pathlib import Path

import pytest
from aws_cdk import Stack, aws_lambda

from cdk_pyproject import PyProject


def test_pyproject(capsys: pytest.CaptureFixture[str]) -> None:
    project = PyProject.from_pyproject(str(Path(__file__).with_name("testproject")))
    assert project.runtime.runtime_equals(aws_lambda.Runtime.PYTHON_3_11)

    stack = Stack()
    aws_lambda.Function(
        stack,
        "TestLambda",
        code=project.code(),
        handler="lambda_.lambda_handler",
        runtime=project.runtime,
    )

    captured = capsys.readouterr()
    assert "Installed 2 packages" in captured.err


def test_rye(capsys: pytest.CaptureFixture[str]) -> None:
    project = PyProject.from_rye(str(Path(__file__).with_name("testproject-rye")))
    assert project.runtime.runtime_equals(aws_lambda.Runtime.PYTHON_3_12)

    stack = Stack()
    aws_lambda.Function(
        stack,
        "TestLambda1",
        code=project.code("app/lambda-1"),
        handler="lambda_1.lambda_handler",
        runtime=project.runtime,
    )
    captured = capsys.readouterr()
    assert "Installed 1 package" in captured.err

    aws_lambda.Function(
        stack,
        "TestLambda2",
        code=project.code("app/lambda-2"),
        handler="lambda_2.lambda_handler",
        runtime=project.runtime,
    )
    captured = capsys.readouterr()
    assert "Installed 3 packages" in captured.err


def test_uv(capsys: pytest.CaptureFixture[str]) -> None:
    project = PyProject.from_uv(str(Path(__file__).with_name("testproject-uv")))
    assert project.runtime.runtime_equals(aws_lambda.Runtime.PYTHON_3_12)

    stack = Stack()
    aws_lambda.Function(
        stack,
        "TestLambda1",
        code=project.code("app/uv-lambda-1"),
        handler="uv_lambda_1.lambda_handler",
        runtime=project.runtime,
    )
    captured = capsys.readouterr()
    assert "Installed 1 package" in captured.err

    aws_lambda.Function(
        stack,
        "TestLambda2",
        code=project.code("app/uv-lambda-2"),
        handler="uv_lambda_2.lambda_handler",
        runtime=project.runtime,
    )
    captured = capsys.readouterr()
    assert "Installed 3 packages" in captured.err


def test_script(capsys: pytest.CaptureFixture[str]) -> None:
    project = PyProject.from_script(str(Path(__file__).with_name("script.py")))
    assert project.runtime.runtime_equals(aws_lambda.Runtime.PYTHON_3_11)

    stack = Stack()
    aws_lambda.Function(
        stack,
        "TestLambda",
        code=project.code(),
        handler="lambda_.lambda_handler",
        runtime=project.runtime,
    )

    captured = capsys.readouterr()
    assert "Installed 6 packages" in captured.err
    assert "cp script.py /asset-output" in captured.err
