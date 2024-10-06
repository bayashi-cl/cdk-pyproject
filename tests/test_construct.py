from pathlib import Path

import pytest
from aws_cdk import Stack, aws_lambda

from cdk_pyproject import PyProject, PyScript


def test_pyproject(capsys: pytest.CaptureFixture[str]) -> None:
    project = PyProject.from_pyproject(str(Path(__file__).with_name("testproject")))
    assert project.runtime.runtime_equals(aws_lambda.Runtime.PYTHON_3_11)

    aws_lambda.Function(
        Stack(),
        "TestLambda",
        code=project.code(),
        handler="dummy.handler",
        runtime=project.runtime,
    )
    captured = capsys.readouterr()
    assert "Successfully installed peppercorn-0.6 testproject-0.1.0" in captured.err


def test_rye(capsys: pytest.CaptureFixture[str]) -> None:
    project = PyProject.from_rye(str(Path(__file__).with_name("testproject-rye")))
    stack = Stack()
    aws_lambda.Function(
        stack,
        "TestLambda1",
        code=project.code("lambda-1"),
        handler="lambda_1.lambda_handler",
        runtime=project.runtime,
    )
    captured = capsys.readouterr()
    assert "Successfully installed lambda-1-0.1.0" in captured.err

    aws_lambda.Function(
        stack,
        "TestLambda2",
        code=project.code("lambda-2"),
        handler="lambda_2.lambda_handler",
        runtime=project.runtime,
    )
    captured = capsys.readouterr()
    assert "Successfully installed lambda-2-0.1.0 peppercorn-0.6" in captured.err


def test_uv(capsys: pytest.CaptureFixture[str]) -> None:
    project = PyProject.from_uv(str(Path(__file__).with_name("testproject-uv")))
    stack = Stack()
    aws_lambda.Function(
        stack,
        "TestLambda1",
        code=project.code("uv-lambda-1"),
        handler="uv_lambda_1.lambda_handler",
        runtime=project.runtime,
    )
    captured = capsys.readouterr()
    assert "Successfully installed uv-lambda-1-0.1.0" in captured.err

    aws_lambda.Function(
        stack,
        "TestLambda2",
        code=project.code("uv-lambda-2"),
        handler="uv_lambda_2.lambda_handler",
        runtime=project.runtime,
    )
    captured = capsys.readouterr()
    assert "Successfully installed peppercorn-0.6 uv-lambda-1-0.1.0 uv-lambda-2-0.1.0" in captured.err


def test_script(capsys: pytest.CaptureFixture[str]) -> None:
    script = PyScript.from_script(str(Path(__file__).with_name("script.py")))
    assert script.runtime.runtime_equals(aws_lambda.Runtime.PYTHON_3_11)
    aws_lambda.Function(
        Stack(),
        "ScriptLambda",
        code=script.code(),
        handler="script.handler",
        runtime=script.runtime,
    )
    captured = capsys.readouterr()
    assert "Successfully installed" in captured.err
