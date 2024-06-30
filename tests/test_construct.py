from pathlib import Path

import pytest
from aws_cdk import App, Stack, aws_lambda
from cdk_pyproject import PyProject
from constructs import Construct


@pytest.mark.parametrize(
    "target",
    [
        Path(__file__).with_name("testproject"),
    ],
)
def test_build(target: Path) -> None:
    class TestStack(Stack):
        def __init__(self, scope: Construct, construct_id: str) -> None:
            super().__init__(scope, construct_id)

            project = PyProject.from_pyproject(str(target))
            aws_lambda.Function(
                self,
                "TestLambda",
                code=project.code(),
                handler="dummy.handler",
                runtime=project.runtime,
            )

    TestStack(App(), TestStack.__name__)
