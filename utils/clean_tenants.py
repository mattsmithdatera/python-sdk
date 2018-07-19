#!/usr/bin/env python
from __future__ import (print_function, unicode_literals, division,
                        absolute_import)

import sys
import threading

from builtins import input
try:
    import Queue as queue
except ImportError:
    import queue

import dfs_sdk
from dfs_sdk import scaffold


def _deleter(args, api, q):
    while True:
        tenant = q.get()
        tpath = tenant['path']
        apps = api.app_instances.list(tenant=tpath)
        inits = api.initiators.list(tenant=tpath)
        if ((args.non_empty or len(apps) == 0) and
                args.clean):
            for ai in apps:
                ai.set(admin_state='offline',
                       force=True,
                       tenant=tpath)
                ai.delete(tenant=tpath)
            for init in inits:
                if init.tenant == tenant:
                    try:
                        init.delete(tenant=tpath, force=True)
                    except dfs_sdk.exceptions.ApiInvalidRequestError as e:
                        print(e)
                    except dfs_sdk.exceptions.ApiNotFoundError as e:
                        print(e)
            if args.openstack_only and tenant['name'].startswith("OS-"):
                print("Openstack Tenant: ", tpath)
                try:
                    tenant.delete(tenant=tpath)
                except dfs_sdk.exceptions.ApiInvalidRequestError as e:
                    print(e)
            elif not args.openstack_only:
                print("Tenant", tpath)
                try:
                    tenant.delete(tenant=tpath)
                except dfs_sdk.exceptions.ApiInvalidRequestError as e:
                    print(e)
            q.task_done()


def main(args):
    api = scaffold.get_api()
    to_delete = queue.Queue()
    for tenant in api.tenants.list():
        if tenant['path'].endswith('root'):
            continue
        if args.openstack_only and not tenant['name'].startswith('OS-'):
            continue
        to_delete.put(tenant)
    yes = False
    if args.yes:
        yes = True
    else:
        newq = queue.Queue()
        while True:
            try:
                tenant = to_delete.get(block=False)
            except queue.Empty:
                break
            print(tenant['path'])
            newq.put(tenant)
        to_delete = newq
        resp = input("Are you sure you want to delete these? [Y/N]\n")
        if resp.strip() in ("Y", "yes"):
            yes = True

    if yes:
        print("Deleting")
        for _ in args.workers:
            thread = threading.Thread(target=_deleter,
                                      args=(args, api, to_delete))
            thread.daemon = True
            thread.start()
        to_delete.join()
        sys.exit(0)
    else:
        print("Cancelling")
        sys.exit(1)


if __name__ == "__main__":
    parser = scaffold.get_argparser()
    parser.add_argument("-c", "--clean", action='store_true',
                        help="Clean empty tenants")
    parser.add_argument("-o", "--openstack-only", action='store_true',
                        help="Clean only openstack tenants")
    parser.add_argument("-y", "--yes", action='store_true',
                        help="DANGER!!! Bypass confirmation prompt")
    parser.add_argument("-n", "--non-empty", action='store_true',
                        help="Clean non-empty tenants as well")
    parser.add_argument("-w", "--workers", default=5)
    args = parser.parse_args()
    main(args)
    sys.exit(0)
