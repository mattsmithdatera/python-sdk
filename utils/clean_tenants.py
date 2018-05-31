#!/usr/bin/env python
from __future__ import (print_function, unicode_literals, division,
                        absolute_import)

import sys

from builtins import input

from dfs_sdk import scaffold


def main(args):
    api = scaffold.get_api()
    to_delete = []
    for tenant in api.tenants.list():
        if tenant['path'].endswith('root'):
            continue
        tpath = tenant['path']
        if ((not api.app_instances.list(tenant=tpath) or args.non_empty) and
                args.clean):
            if args.openstack_only:
                if tenant['name'].startswith("OS-"):
                    print("Openstack Tenant: ", tpath)
                    to_delete.append(tenant)
            else:
                print("Tenant", tpath)
                to_delete.append(tenant)
    yes = False
    if args.yes:
        yes = True
    else:
        resp = input("Are you sure you want to delete these? [Y/N]\n")
        if resp.strip() in ("Y", "yes"):
            yes = True

    if yes:
        print("Deleting")
        for t in to_delete:
            for ai in api.app_instances.list(tenant=t['path']):
                ai.set(admin_state="offline", tenant=t['path'], force=True)
                ai.delete(tenant=t['path'])
            t.delete()
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
    args = parser.parse_args()
    main(args)
    sys.exit(0)
