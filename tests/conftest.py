import mock
import pytest

from dfs_sdk import get_api
from dfs_sdk.connection import ApiConnection
from dfs_sdk.context import ApiContext
from tests.utils import load_asset


@pytest.fixture
def mock_api_21():
    api = get_api('1.1.1.1',
                  'admin',
                  'password',
                  version="v2.1",
                  tenant='test',
                  timeout=0.01,
                  immediate_login=False)
    http = mock.Mock()
    ctxt_mock = ApiContext()
    ctxt_mock.hostname = "testhost"
    ctxt_mock.version = "v2.1"
    ctxt_mock.username = "admin"
    ctxt_mock.password = "password"
    ctxt_mock._reader = mock.Mock()
    con = ApiConnection(ctxt_mock)
    # resp_data = load_asset("api_endpoint_21.txt")
    http.side_effect = [(b'{"key": "84c457eb414c4ab5a472292c4bc2b1c1",'
                        b'"version": "v2.1"}', 200, "", {})]
    con._http_connect_request = http
    ctxt_mock.connection = con
    ctxt_mock.reader._ep_name_set.__contains__ = lambda a, b: True
    api._context = ctxt_mock
    return api, http
