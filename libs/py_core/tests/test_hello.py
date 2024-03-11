"""Hello unit test module."""

from libs.py_core.py_core.hello import hello


def test_hello():
    """Test the hello function."""
    assert hello() == "Hello py-core"
