#!/usr/bin/env python
from __future__ import (print_function, unicode_literals, division,
                        absolute_import)

import argparse
import io
import re
import sys
import threading
try:
    from Queue import Queue
except ImportError:
    from queue import Queue

from dfs_sdk import get_api

IPRE_STR = r'(\d{1,3}\.){3}\d{1,3}'
IPRE = re.compile(IPRE_STR)

SIP = re.compile(r'san_ip\s+?=\s+?(?P<san_ip>%s)' % IPRE_STR)
SLG = re.compile(r'san_login\s+?=\s+?(?P<san_login>.*)')
SPW = re.compile(r'san_password\s+?=\s+?(?P<san_password>.*)')


def readCinderConf():
    data = None
    with io.open('/etc/cinder/cinder.conf') as f:
        data = f.read()
    san_ip = SIP.search(data).group('san_ip')
    san_login = SLG.search(data).group('san_login')
    san_password = SPW.search(data).group('san_password')
    return san_ip, san_login, san_password


def getAPI(san_ip, san_login, san_password, version, tenant=None):
    if not any((san_ip, san_login, san_password)):
        san_ip, san_login, san_password = readCinderConf()
    if tenant and "root" not in tenant:
        tenant = "/root/{}".format(tenant)
    return get_api(san_ip,
                   san_login,
                   san_password,
                   version,
                   tenant=tenant,
                   secure=True,
                   immediate_login=True)


def _worker(api, queue):
    while not queue.empty():
        name, size, replica_count = queue.get()
        print("Creating AppInstance:", name)
        ai = api.app_instances.create(name=name)
        si = ai.storage_instances.create(name="storage-1")
        si.volumes.create(name="volume-1", size=size,
                          replica_count=replica_count)
        queue.task_done()


def main(args):
    api = getAPI(args.hostname, args.username, args.password, args.api_version)

    # Populate Queue
    ai_names = Queue()
    for i in range(args.number):
        name = "-".join((args.prefix, str(i)))
        ai_names.put((name, args.size, args.replica_count))

    for _ in range(args.threads):
        thread = threading.Thread(target=_worker,
                                  args=(api, ai_names))
        thread.daemon = True
        thread.start()

    ai_names.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--number", default=5, type=int,
                        help="Number of AppInstances")
    parser.add_argument("-s", "--size", default=1, type=int,
                        help="Size of AppInstances")
    parser.add_argument("-p", "--prefix", default="my-app",
                        help="Prefix each AppInstance should use")
    parser.add_argument("-r", "--replica-count", default=3, type=int,
                        help="Number of replicas for volumes, default: 3")
    parser.add_argument("-m", "--threads", default=5,
                        help="Threads to use for deletion")
    parser.add_argument("--hostname")
    parser.add_argument("--username")
    parser.add_argument("--password")
    parser.add_argument("--api-version", default="v2.1")
    args = parser.parse_args()

    main(args)
    sys.exit(0)
