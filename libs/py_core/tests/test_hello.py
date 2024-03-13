"""Hello unit test module."""

import pytest
from libs.py_core.py_core.hello import hello
from libs.py_core.py_core.system.processor import ChildCardRecommendationGenerator


def test_hello():
    """Test the hello function."""
    assert hello() == "Hello py-core"

