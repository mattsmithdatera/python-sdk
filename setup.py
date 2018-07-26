#!/usr/bin/env python

import io
import os
import re

from setuptools import setup, find_packages

CONSTANTS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'src', 'dfs_sdk', 'constants.py')

VRE = re.compile("""VERSION = ['"](.*)['"]""")


def get_version():
    with io.open(CONSTANTS_FILE) as f:
        return VRE.search(f.read()).group(1)


version = get_version()

setup(
    name='dfs_sdk',
    version=version,
    description='Datera Fabric Python SDK',
    long_description='Install Instructions: sudo python setup.py install',
    author='Datera Automation Team',
    author_email='support@datera.io',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data={'dfs_sdk': ['log_cfg/*.json']},
    include_package_data=True,
    install_requires=[],
    scripts=['utils/dhutil'],
    url='https://github.com/Datera/python-sdk/',
    download_url='https://github.com/Datera/python-sdk/tarball/v{}'.format(
        version)
)
