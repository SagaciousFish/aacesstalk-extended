"""Hello unit test module."""

from aacesstalk_backend.hello import hello


def test_hello():
    """Test the hello function."""
    assert hello() == "Hello aacesstalk-backend"
