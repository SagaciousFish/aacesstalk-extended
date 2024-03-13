"""Hello unit test module."""

import pytest
from py_core.hello import hello
from py_core.system.processor import ChildCardRecommendationGenerator


def test_hello():
    """Test the hello function."""
    assert hello() == "Hello py-core"

