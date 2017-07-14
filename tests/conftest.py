import mock
import pytest

from dfs_sdk import get_api


@pytest.fixture
def mock_api_21():
    con = mock.Mock()
    con.side_effect = [(b'{"key": "84c457eb414c4ab5a472292c4bc2b1c1",'
                        b'"version": "v2.1"}', 200, "", {})]
    api = get_api('1.1.1.1',
                  'admin',
                  'password',
                  version="v2.1",
                  tenant='test',
                  timeout=0.01,
                  immediate_login=False)
    api._context.connection._http_connect_request = con
    return api, con
