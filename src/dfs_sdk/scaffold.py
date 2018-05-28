from __future__ import (print_function, unicode_literals, division,
                        absolute_import)

import argparse
import io
import json
import os
import re

from dfs_sdk import get_api

IPRE_STR = r'(\d{1,3}\.){3}\d{1,3}'
IPRE = re.compile(IPRE_STR)

SIP = re.compile(r'san_ip\s+?=\s+?(?P<san_ip>%s)' % IPRE_STR)
SLG = re.compile(r'san_login\s+?=\s+?(?P<san_login>.*)')
SPW = re.compile(r'san_password\s+?=\s+?(?P<san_password>.*)')
TNT = re.compile(r'datera_tenant_id\s+?=\s+?(?P<tenant_id>.*)')

LATEST = "2.2"

UNIX_HOME = os.path.join(os.path.expanduser('~'))
UNIX_CONFIG_HOME = os.path.join(UNIX_HOME, 'datera')
UNIX_SITE_CONFIG_HOME = '/etc/datera'
CONFIG_SEARCH_PATH = [os.getcwd(), UNIX_HOME, UNIX_CONFIG_HOME,
                      UNIX_SITE_CONFIG_HOME]
CONFIGS = [".datera-config", "datera-config", ".datera-config.json",
           "datera-config.json"]


def search_config():
    for p in CONFIG_SEARCH_PATH:
        for conf in CONFIGS:
            fpath = os.path.join(p, conf)
            if os.path.exists(fpath):
                return fpath
    read_cinder_conf()
    raise EnvironmentError("Could not find Datera config file in the following"
                           " locations: [{}]".format(CONFIG_SEARCH_PATH))


def read_config():
    try:
        config_file = search_config()
    except EnvironmentError:
        return None
    with io.open(config_file) as f:
        return json.loads(f.read())


def read_cinder_conf():
    data = None
    found_index = 0
    found_last_index = -1
    with io.open('/etc/cinder/cinder.conf') as f:
        for index, line in enumerate(f):
            if '[datera]' == line.strip().lower():
                found_index = index
                break
        for index, line in enumerate(f):
            if '[' in line and ']' in line:
                found_last_index = index + found_index
                break
    with io.open('/etc/cinder/cinder.conf') as f:
        data = "".join(f.readlines()[
            found_index:found_last_index])
    san_ip = SIP.search(data).group('san_ip')
    san_login = SLG.search(data).group('san_login')
    san_password = SPW.search(data).group('san_password')
    tenant = TNT.search(data)
    if tenant:
        tenant = tenant.group('tenant_id')
    return san_ip, san_login, san_password, tenant


def getAPI(san_ip, san_login, san_password, version=None, tenant=None):
    try:
        if not all((san_ip, san_login, san_password, tenant)):
            csan_ip, csan_login, csan_password, ctenant = read_cinder_conf()
            # Set from cinder.conf if they don't exist
            # This allows overriding some values in cinder.conf
            if not tenant:
                tenant = ctenant
            if not san_ip:
                san_ip = csan_ip
            if not san_login:
                san_login = csan_login
            if not san_password:
                san_password = csan_password
            if tenant and "root" not in tenant and tenant != "all":
                tenant = "/root/{}".format(tenant)
            if not tenant:
                tenant = "/root"
            if not version:
                version = "v{}".format(LATEST)
            else:
                version = "v{}".format(version.strip("v"))
    except IOError:
        pass
    return get_api(san_ip,
                   san_login,
                   san_password,
                   version,
                   tenant=tenant,
                   secure=True,
                   immediate_login=True)


def get_argparser():
    parser = argparse.ArgumentParser()
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
    args, _ = parser.parse_known_args()
    config = read_config()
    if not config:
        raise
    parser = argparse.ArgumentParser(parents=[parser])
    return parser
