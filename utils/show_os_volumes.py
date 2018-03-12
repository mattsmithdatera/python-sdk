#!/usr/bin/env python

from __future__ import (print_function, unicode_literals, division,
                        absolute_import)

import argparse
import os
import sys

from openstack import connection

from scaffold import getAPI

verbose = False


def usage():
    print("OS_USERNAME, OS_PASSWORD, OS_AUTH_URL and "
          "OS_PROJECT_NAME must be set")


def vprint(*args, **kwargs):
    global verbose
    if verbose:
        print(*args, **kwargs)


def get_conn(project_name=None, username=None, password=None, udomain=None,
             pdomain=None):
    auth_dict = {'auth_url': os.getenv("OS_AUTH_URL"),
                 'project_name': project_name if project_name else os.getenv(
                     "OS_PROJECT_NAME"),
                 'username': username if username else os.getenv(
                     "OS_USERNAME"),
                 'password': password if password else os.getenv(
                     "OS_PASSWORD"),
                 'user_domain_id': udomain if udomain else os.getenv(
                     "OS_USER_DOMAIN_ID"),
                 'project_domain_id': pdomain if pdomain else os.getenv(
                     "OS_PROJECT_DOMAIN_ID")}

    if not all(auth_dict.keys()):
        usage()
        sys.exit(1)
    return connection.Connection(**auth_dict)


def create_volume(conn, size, vol_ref=None, vols=None, image_name=None,
                  volume_type=None):
    global image_id
    imid = None
    if not vol_ref:
        imid = image_id
    vprint("Creating Volume: size={}, vol_ref={}, image_name={}, "
           "volume_type={}".format(size, vol_ref, image_name, volume_type))
    vol_id = conn.block_storage.create_volume(size=size,
                                              imageRef=imid,
                                              source_volid=vol_ref,
                                              volume_type='datera').id
    vprint("Created Volume: {}".format(vol_id))
    while True:
        vol = conn.block_storage.get_volume(vol_id)
        if vol.status == 'available':
            if vols:
                vols.put(vol)
            vprint("Volume: {} now available".format(vol_id))
            return vol


def main(args):

    global verbose, net_name, netns
    if args.verbose:
        verbose = True

    api = getAPI(args.san_ip,
                 args.san_login,
                 args.san_password,
                 args.api_version,
                 args.tenant)

    conn = get_conn()

    vols = {"OS-{}".format(vol.id) for vol in conn.block_storage.volumes()}
    vols = vols.union({"OS-{}".format(img.id) for img in conn.image.images()})
    ais = api.app_instances.list()

    non_os = set()
    for ai in ais:
        if ai['name'] not in vols:
            non_os.add(ai['name'])

    print("Datera OpenStack AIs")
    print("--------------------")
    for ai in sorted(vols):
        print(ai)
    print("\nDatera Non-OpenStack AIs")
    print("------------------------")
    for ai in sorted(non_os):
        print(ai)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--san-ip')
    parser.add_argument('--san_login')
    parser.add_argument('--san_password')
    parser.add_argument('--api-version')
    parser.add_argument('--tenant')
    parser.add_argument('-v', '--verbose', default=False, action='store_true',
                        help="Enable verbose output")

    args = parser.parse_args()

    sys.exit(main(args))
