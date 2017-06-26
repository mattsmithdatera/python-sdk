import io
import mock
import os
import pytest


DATA = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'data')


def load_asset(name):
    n = os.path.join(DATA, name)
    with io.open(n) as f:
        return f.read()


def test_import():
    from dfs_sdk import DateraApi  # noqa
    from dfs_sdk import DateraApi21  # noqa


def test_failed_import():
    with pytest.raises(ImportError):
        from dfs_sdk import NotDateraApi  # noqa


def test_get_api():
    from dfs_sdk import get_api
    with mock.patch('dfs_sdk.DateraApi'):
        get_api("1.1.1.1", "admin", "password", "v2")
    with mock.patch('dfs_sdk.DateraApi21'):
        get_api("1.1.1.1", "admin", "password", "v2.1")
    with pytest.raises(NotImplementedError):
        get_api("1.1.1.1", "admin", "password", "v1.0")


def test_exception_imports():
    from dfs_sdk import ApiError  # noqa
    from dfs_sdk import ApiAuthError  # noqa
    from dfs_sdk import ApiInvalidRequestError  # noqa
    from dfs_sdk import ApiNotFoundError  # noqa
    from dfs_sdk import ApiConflictError  # noqa
    from dfs_sdk import ApiConnectionError  # noqa
    from dfs_sdk import ApiTimeoutError  # noqa
    from dfs_sdk import ApiInternalError  # noqa
    from dfs_sdk import ApiUnavailableError  # noqa


def test_api_21_mocks(mock_api_21):
    api = mock_api_21
    api.app_instances.list()


def test_api_21_ai_list(mock_api_21):
    api = mock_api_21
    resp_data = load_asset("test_api_21_ai_list.txt")
    print(api.app_instances)
