"""
Python package for interacting with the REST interface of a Datera
storage cluster.
"""
from __future__ import (print_function, absolute_import, unicode_literals,
                        division)
# Renaming imports to prevent easy top-level importing
# We want folks to use get_api(), not these object directly
from .api import DateraApi as _DateraApi
from .api import DateraApi21 as _DateraApi21
from .api import DateraApi22 as _DateraApi22

from .constants import API_VERSIONS
from .exceptions import ApiError
from .exceptions import ApiAuthError
from .exceptions import ApiInvalidRequestError
from .exceptions import ApiNotFoundError
from .exceptions import ApiConflictError
from .exceptions import ApiConnectionError
from .exceptions import ApiTimeoutError
from .exceptions import ApiInternalError
from .exceptions import ApiUnavailableError
from .dlogging import setup_logging
from .hooks.base import load_hooks


__copyright__ = "Copyright 2017, Datera, Inc."


# TODO(mss): generate this from version list imported from constants
VERSION_MAP = {"v2": _DateraApi,
               "v2.1": _DateraApi21,
               "v2.2": _DateraApi22}


def get_api(hostname, username, password, version, tenant=None, strict=True,
            hooks=None, **kwargs):
    """Main entrypoint into the SDK

    Returns a DateraApi object
    Parameters:
      hostname (str) - The hostname or VIP
      username (str) - e.g. "admin"
      password (str)
      version (str) - must be in constants.API_VERSIONS
    Optional parameters:
      tenant (str) - Tenant, for v2.1+ API only
    """
    setup_logging(kwargs.get('disable_log', False))
    if version not in API_VERSIONS:
        raise ValueError(
            "API version {} unsupported by SDK at this time. Supported "
            "versions: {}".format(version, API_VERSIONS))
    if version == "v2" and tenant:
        raise ValueError("API version v2 does not support multi-tenancy")
    api = VERSION_MAP[version](hostname,
                               username=username,
                               password=password,
                               tenant=tenant,
                               strict=strict,
                               **kwargs)
    if hooks:
        load_hooks(api, hooks)
    return api


__all__ = ['get_api',
           'ApiError',
           'ApiAuthError',
           'ApiInvalidRequestError',
           'ApiNotFoundError',
           'ApiConflictError',
           'ApiConnectionError',
           'ApiTimeoutError',
           'ApiInternalError',
           'ApiUnavailableError']
