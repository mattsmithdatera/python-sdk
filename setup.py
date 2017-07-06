#!/usr/bin/env

from setuptools import setup, find_packages

setup(
    name='dfs_sdk',
    version='1.2.1',
    description='Datera Fabric Python SDK',
    long_description='Install Instructions: sudo python setup.py install',
    author='Datera Automation Team',
    author_email='support@datera.io',
    packages=find_packages('src'),
    package_dir={'dfs_sdk': 'src/dfs_sdk'},
    package_data={'dfs_sdk': ['log_cfg/*.json']},
    include_package_data=True,
    install_requires=[],
    scripts=['utils/dhutil'],
    url='https://github.com/Datera/python-sdk/',
    download_url='https://github.com/Datera/python-sdk/tarball/v1.2.1'
)
