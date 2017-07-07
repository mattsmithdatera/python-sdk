import itertools
import pytest

from tests.utils import load_asset


def update_side_effect(mock, *args):
    mock.side_effect = itertools.chain(mock.side_effect, args)


def test_import():
    from dfs_sdk import get_api  # noqa


def test_failed_import():
    # We don't allow importing the direct classes
    with pytest.raises(ImportError):
        from dfs_sdk import DateraApi  # noqa
        from dfs_sdk import DateraApi21  # noqa
        from dfs_sdk import DateraApi22  # noqa


def test_get_api():
    from dfs_sdk import get_api
    get_api("1.1.1.1", "admin", "password", "v2", timeout=0.01,
            immediate_login=False)
    get_api("1.1.1.1", "admin", "password", "v2.1", timeout=0.01,
            immediate_login=False)
    with pytest.raises(ValueError):
        get_api("1.1.1.1", "admin", "password", "v1.0", timeout=0.01,
                immediate_login=False)


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
    api, con = mock_api_21
    resp = b"""
        {
      "tenant": "/root",
      "path": "/app_instances",
      "version": "v2.1",
      "data": [],
      "metadata": {
        "total": 0
      }
    }
    """
    update_side_effect(con, (resp, 200, "", {}))
    api.app_instances.list()


def test_api_21_ai_list(mock_api_21):
    api, con = mock_api_21
    resp_data = load_asset("test_api_21_ai_list.txt")
    update_side_effect(con, (resp_data, 200, "", {}))
    ais = api.app_instances.list()
    assert len(ais) == 2
    ai1, ai2 = ais
    assert ai1['name'] == 'test-app-1'
    assert ai2['name'] == 'test-app-2'


def test_api_21_si_list(mock_api_21):
    api, con = mock_api_21
    resp_data = load_asset("test_api_21_si_list_0.txt")
    resp_data2 = load_asset("test_api_21_si_list_1.txt")
    update_side_effect(
        con, (resp_data, 200, "", {}), (resp_data2, 200, "", {}))
    ai = api.app_instances.list()[0]
    sis = ai.storage_instances.list()
    assert len(sis) == 1
    assert sis[0]['name'] == 'storage-1'


def test_api_21_vol_list(mock_api_21):
    api, con = mock_api_21
    resp_data = load_asset("test_api_21_vol_list_0.txt")
    resp_data2 = load_asset("test_api_21_vol_list_1.txt")
    resp_data3 = load_asset("test_api_21_vol_list_2.txt")
    update_side_effect(
        con,
        (resp_data, 200, "", {}),
        (resp_data2, 200, "", {}),
        (resp_data3, 200, "", {}))
    ai = api.app_instances.list()[0]
    si = ai.storage_instances.list()[0]
    vols = si.volumes.list()
    assert len(vols) == 1
    assert vols[0]['name'] == 'volume-1'


# def test_schema():
#     from dfs_sdk.schema.reader import Reader21
#     import requests
#     data = requests.get("http://172.19.1.41:7717/v2.1/api").json()
#     r = Reader21(data)
#     for endpoint in r._endpoints:
#         print(r._normalize(endpoint))
