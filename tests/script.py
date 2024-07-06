# ruff: noqa
# /// script
# requires-python = ">=3.11,<3.12"
# dependencies = [
#   "requests<3",
#   "peppercorn",
# ]
# ///

from typing import Any

import requests  # type: ignore


def handler(event: Any, context: Any) -> Any:
    resp = requests.get("https://peps.python.org/api/peps.json", timeout=30)
    data = resp.json()
    return [(k, v["title"]) for k, v in data.items()][:10]
