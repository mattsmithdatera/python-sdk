from __future__ import (print_function, unicode_literals, division,
                        absolute_import)

import argparse
import copy
import io
import json
import os
import re
import pprint

from dfs_sdk import get_api as _get_api

IPRE_STR = r'(\d{1,3}\.){3}\d{1,3}'
IPRE = re.compile(IPRE_STR)

SIP = re.compile(r'san_ip\s+?=\s+?(?P<san_ip>%s)' % IPRE_STR)
SLG = re.compile(r'san_login\s+?=\s+?(?P<san_login>.*)')
SPW = re.compile(r'san_password\s+?=\s+?(?P<san_password>.*)')
TNT = re.compile(r'datera_tenant_id\s+?=\s+?(?P<tenant_id>.*)')

LATEST = "2.2"
FALLBACK = ["2", "2.1"]

UNIX_HOME = os.path.join(os.path.expanduser('~'))
UNIX_CONFIG_HOME = os.path.join(UNIX_HOME, 'datera')
UNIX_SITE_CONFIG_HOME = '/etc/datera'
CONFIG_SEARCH_PATH = [os.getcwd(), UNIX_HOME, UNIX_CONFIG_HOME,
                      UNIX_SITE_CONFIG_HOME]
CONFIGS = [".datera-config", "datera-config", ".datera-config.json",
           "datera-config.json"]
CINDER_ETC = "/etc/cinder/cinder.conf"

EXAMPLE_CONFIG = {"mgmt_ip": "1.1.1.1",
                  "username": "admin",
                  "password": "password",
                  "tenant": None}

_CONFIG = {}
_ARGS = None
VERBOSE = False


def vprint(*args, **kwargs):
    global VERBOSE
    if VERBOSE:
        print(*args, **kwargs)


def _search_config():
    for p in CONFIG_SEARCH_PATH:
        for conf in CONFIGS:
            fpath = os.path.join(p, conf)
            if os.path.exists(fpath):
                return fpath
    if not os.path.exists(CINDER_ETC):
        raise EnvironmentError(
            "Could not find Datera config file in the following"
            " locations: [{}]".format(CONFIG_SEARCH_PATH))


def _read_config():
    global _CONFIG
    if _ARGS.config:
        config_file = _ARGS.config
    else:
        config_file = _search_config()
    if not config_file:
        _CONFIG = _read_cinder_conf()
    else:
        with io.open(config_file) as f:
            _CONFIG = json.loads(f.read())


def _read_cinder_conf():
    if not os.path.exists(CINDER_ETC):
        return
    data = None
    found_index = 0
    found_last_index = -1
    with io.open(CINDER_ETC) as f:
        for index, line in enumerate(f):
            if '[datera]' == line.strip().lower():
                found_index = index
                break
        for index, line in enumerate(f):
            if '[' in line and ']' in line:
                found_last_index = index + found_index
                break
    with io.open(CINDER_ETC) as f:
        data = "".join(f.readlines()[
            found_index:found_last_index])
    san_ip = SIP.search(data).group('san_ip')
    san_login = SLG.search(data).group('san_login')
    san_password = SPW.search(data).group('san_password')
    tenant = TNT.search(data)
    if tenant:
        tenant = tenant.group('tenant_id')
    return {"mgmt_ip": san_ip,
            "username": san_login,
            "password": san_password,
            "tenant": tenant,
            "api_version": LATEST}


def _cli_override():
    if _ARGS.hostname:
        _CONFIG["mgmt_ip"] = _ARGS.hostname
    if _ARGS.username:
        _CONFIG["username"] = _ARGS.username
    if _ARGS.password:
        _CONFIG["password"] = _ARGS.password
    if _ARGS.tenant:
        _CONFIG["tenant"] = _ARGS.tenant
    if _ARGS.api_version:
        _CONFIG["api_version"] = _ARGS.api_version


def get_api():
    _read_config()
    _cli_override()
    tenant = _CONFIG["tenant"]
    if tenant and "root" not in tenant and tenant != "all":
        tenant = "/root/{}".format(tenant)
    if not tenant:
        tenant = "/root"
    if not _CONFIG["api_version"]:
        version = "v{}".format(LATEST)
    else:
        version = "v{}".format(_CONFIG["api_version"].strip("v"))
    return _get_api(_CONFIG["mgmt_ip"],
                    _CONFIG["username"],
                    _CONFIG["password"],
                    version,
                    tenant=tenant,
                    secure=True,
                    immediate_login=True)


def print_config():
    config = copy.deepcopy(_CONFIG)
    config["password"] = "******"
    pprint.pprint(config)


def get_config():
    return copy.deepcopy(_CONFIG)


def get_argparser():
    global _ARGS, VERBOSE
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--api-version", default="v{}".format(LATEST),
                        help="Datera API version to use (default={})".format(
                            LATEST))
    parser.add_argument("--hostname", help="Hostname or IP Address of Datera "
                                           "backend")
    parser.add_argument("--username", help="Username for Datera account")
    parser.add_argument("--password", help="Password for Datera account")
    parser.add_argument("--tenant", action="append", default=[],
                        help="Tenant Name/ID to search under,"
                             " use 'all' for all tenants")
    parser.add_argument("--config", help="Config file location")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose output")
    args, _ = parser.parse_known_args()
    _ARGS = args
    VERBOSE = args.verbose
    new_parser = argparse.ArgumentParser(parents=[parser])
    return new_parser
