#!/usr/bin/env python
from __future__ import (print_function, unicode_literals, division,
                        absolute_import)

import argparse
import re
import sys
import threading
import time
try:
    from Queue import Queue
except ImportError:
    from queue import Queue

from builtins import input

from dfs_sdk.scaffold import getAPI


def _add_worker(queue, to_delete, api, filters):
    while not queue.empty():
        tenant = queue.get()
        ais = api.app_instances.list(tenant=tenant)
        for ai in ais:
            if any((compf.match(ai['name']) for compf in filters)):
                to_delete.add((ai['name'], ai['path'], tenant))
        queue.task_done()


def _del_worker(queue, api):
    # Give time for the queue to fill
    time.sleep(0.2)
    while not queue.empty():
        _, path, tenant = queue.get()
        ai = api.app_instances.entity_from_path(path, tenant=tenant)
        print("Deleting: ", ai['name'])
        ai.set(admin_state="offline", force=True, tenant=tenant)
        ai.delete(tenant=tenant)
        queue.task_done()


def main(args):
    api = getAPI(args.hostname, args.username, args.password, args.api_version)
    to_delete = set()

    filter_strs = set(args.re_filter)
    filters = []
    if args.all:
        filter_strs.add(".*")

    for f in filter_strs:
        filters.append(re.compile(f))

    tqueue = Queue()
    if args.tenant == "ALL":
        for tenant in api.tenants.list():
            tqueue.put(tenant['path'])
    else:
        for tenant in args.tenant:
            tqueue.put(tenant)

    for _ in range(args.threads):
        thread = threading.Thread(target=_add_worker,
                                  args=(tqueue, to_delete, api, filters))
        thread.daemon = True
        thread.start()

    tqueue.join()

    to_delete_queue = Queue()
    to_delete = sorted(to_delete)
    print("Delete These AppInstances?")
    for ai in to_delete:
        to_delete_queue.put(ai)
        print(ai[0])

    yes = False
    if not args.yes:
        yes = True if input("Y/n\n").strip() in ("Y", "yes") else False

    if yes or args.yes:
        for _ in range(args.threads):
            thread = threading.Thread(target=_del_worker,
                                      args=(to_delete_queue, api))
            thread.daemon = True
            thread.start()

        to_delete_queue.join()

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--re-filter", action="append",
                        help="Regex filter to use when matching AppInstances")
    parser.add_argument("-t", "--tenant", action="append",
                        help="Tenant Name/ID to search under,"
                             " use 'all' for all tenants")
    parser.add_argument("-a", "--all", action='store_true',
                        help="Match all AppInstances")
    parser.add_argument("-y", "--yes", action='store_true',
                        help="DANGER!!! Bypass confirmation prompt")
    parser.add_argument("-m", "--threads", default=5,
                        help="Threads to use for deletion")
    parser.add_argument("--hostname")
    parser.add_argument("--username")
    parser.add_argument("--password")
    parser.add_argument("--api-version", default="v2.1")
    args = parser.parse_args()

    if not args.tenant:
        args.tenant = ['/root']

    tenants = []
    for tenant in args.tenant:
        if tenant == "all":
            tenants = "ALL"
            break
        if "root" not in tenant:
            t = "/root/{}".format(tenant.strip("/"))
            tenants.append(t)
        else:
            tenants.append(tenant)
    args.tenant = tenants

    if not args.re_filter:
        args.re_filter = []

    main(args)
    sys.exit(0)
