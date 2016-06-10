import pytest
from mock import MagicMock as Mock


def test_api_import():

    from dfs_sdk import DateraApi


def test_api_import_failed():

    with pytest.raises(ImportError):
        from dfs_sdk import NotDateraApi

def test_types_import():

    from dfs_sdk import Auth
    auth = Auth(Mock(), Mock({}))
    assert auth is not None
