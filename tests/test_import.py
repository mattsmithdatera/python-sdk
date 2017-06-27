import pytest


def test_import():
    from dfs_sdk import get_api


def test_failed_import():
    # We don't allow importing the direct classes
    with pytest.raises(ImportError):
        from dfs_sdk import DateraApi
