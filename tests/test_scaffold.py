import contextlib
import os
import shutil

import pytest

from tests.utils import DATA, TESTS, CURR

from dfs_sdk import scaffold


@pytest.yield_fixture
def search_path():
    old = scaffold.CONFIG_SEARCH_PATH
    scaffold.CONFIG_SEARCH_PATH = [os.getcwd(), TESTS, DATA]
    yield
    scaffold.CONFIG_SEARCH_PATH = old


@contextlib.contextmanager
def hide_files(files):
    ffs = []
    try:
        for file in files:
            f = os.path.join(DATA, file)
            bak = file + '.bak'
            shutil.move(f, bak)
            ffs.append((f, bak))
        yield
    finally:
        for f, bak in ffs:
            shutil.move(bak, f)


@contextlib.contextmanager
def move_file(file, location):
    ffs = []
    try:
        f = os.path.join(DATA, file)
        fnew = os.path.join(location, file)
        shutil.move(f, fnew)
        ffs.append((f, fnew))
        yield
    finally:
        for f, fnew in ffs:
            shutil.move(fnew, f)


@contextlib.contextmanager
def setenvs(envs):
    try:
        for k, v in envs.items():
            os.environ[k] = v
        yield
    finally:
        for k, v in envs.items():
            del os.environ[k]


def test_config_directory_load_order(search_path):
    with move_file('datera-config.json', CURR):
        with move_file('.datera-config.json', TESTS):
            conf = scaffold.get_config(reset_config=True)
            assert conf["username"] == "D"
    with move_file('.datera-config.json', TESTS):
        conf = scaffold.get_config(reset_config=True)
        assert conf["username"] == "C"


def test_config_name_load_order(search_path):
    conf = scaffold.get_config(reset_config=True)
    assert conf["username"] == "A"
    with hide_files([".datera-config"]):
        conf = scaffold.get_config(reset_config=True)
        assert conf["username"] == "B"
    with hide_files([".datera-config", "datera-config"]):
        conf = scaffold.get_config(reset_config=True)
        assert conf["username"] == "C"
    with hide_files([".datera-config", "datera-config",
                     ".datera-config.json"]):
        conf = scaffold.get_config(reset_config=True)
        assert conf["username"] == "D"


def test_get_api(search_path):
    with move_file('.datera-config.json', CURR):
        api = scaffold.get_api(reset_config=True, immediate_login=False)
        assert api.context.username == "C"


def test_get_api_envs(search_path):
    ip = "123.321.123.321"
    name = "env-test"
    passwd = "test-password-env"
    with setenvs({scaffold.ENV_MGMT: ip,
                  scaffold.ENV_USER: name,
                  scaffold.ENV_PASS: passwd}):
        api = scaffold.get_api(reset_config=True, immediate_login=False)
        assert api.context.hostname == ip
        assert api.context.username == name
        assert api.context.password == passwd


def test_get_api_custom_config_path(search_path):
    with move_file('.datera-config.json', '/tmp'):
        api = scaffold.get_api(
            reset_config=True,
            config='/tmp/.datera-config.json',
            immediate_login=False)
        assert api.context.username == "C"
