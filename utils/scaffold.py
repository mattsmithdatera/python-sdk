from __future__ import (print_function, unicode_literals, division,
                        absolute_import)

import io
import re

from dfs_sdk import get_api

IPRE_STR = r'(\d{1,3}\.){3}\d{1,3}'
IPRE = re.compile(IPRE_STR)

SIP = re.compile(r'san_ip\s+?=\s+?(?P<san_ip>%s)' % IPRE_STR)
SLG = re.compile(r'san_login\s+?=\s+?(?P<san_login>.*)')
SPW = re.compile(r'san_password\s+?=\s+?(?P<san_password>.*)')
TNT = re.compile(r'datera_tenant_id\s+?=\s+?(?P<tenant_id>.*)')


def read_cinder_conf():
    data = None
    with io.open('/etc/cinder/cinder.conf') as f:
        data = f.read()
    san_ip = SIP.search(data).group('san_ip')
    san_login = SLG.search(data).group('san_login')
    san_password = SPW.search(data).group('san_password')
    tenant = TNT.search(data)
    if tenant:
        tenant = tenant.group('tenant_id')
    return san_ip, san_login, san_password, tenant


def getAPI(san_ip, san_login, san_password, version=None, tenant=None):
    if not any((san_ip, san_login, san_password)):
        san_ip, san_login, san_password, tenant = read_cinder_conf()
    if tenant and "root" not in tenant:
        tenant = "/root/{}".format(tenant)
    if not version:
        version = "v2.2"
    return get_api(san_ip,
                   san_login,
                   san_password,
                   version,
                   tenant=tenant,
                   secure=True,
                   immediate_login=True)
