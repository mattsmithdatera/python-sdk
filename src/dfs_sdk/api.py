"""
Provides the DateraApi objects
"""
import threading

from .constants import DEFAULT_HTTP_TIMEOUT
from .connection import ApiConnection
from .context import ApiContext
from .base import Endpoint as _Endpoint

__copyright__ = "Copyright 2017, Datera, Inc."


DEFAULT_API_VERSION = "v2.1"


# Wrapper function to help deduplicate all the code we were getting with the
# different api versions with little to no difference in this class
def _api_getter(base):

    class _DateraBaseApi(base):
        """
        Use this object to talk to the REST interface of a Datera cluster
        """

        def __init__(self, hostname, username=None, password=None, **kwargs):
            """
            Parameters:
              hostname (str) - IP address or host name
              username (str) - Username to log in with, e.g. "admin"
              password (str) - Password to use when logging in to the cluster
              tenant (str) - Tenant, or None
              timeout (float) - HTTP connection  timeout.  If None, use system
                                default.
              secure (boolean) - Use HTTPS instead of HTTP, defaults to HTTPS
              immediate_login (bool) - If True, login when this object is
                                       instantiated, else wait to login until
                                       a request is sent
              ldap_server (string) - LDAP server
            """
            assert self._version is not None

            if not hostname or not username or not password:
                raise ValueError(
                    "hostname, username, and password are required")

            # Create the context object, common to all endpoints and entities:
            kwargs['hostname'] = hostname
            kwargs['username'] = username
            kwargs['password'] = password
            self._kwargs = kwargs
            self._context = None

            immediate_login = kwargs.get('immediate_login', True)
            if immediate_login:
                self.context.connection.login(
                    name=kwargs['username'], password=kwargs['password'])

            # Initialize sub-endpoints:
            super(_DateraBaseApi, self).__init__(self._context, None)

        @property
        def context(self):
            kwargs = self._kwargs
            tenant = kwargs.get('tenant', None)
            timeout = kwargs.get('timeout', DEFAULT_HTTP_TIMEOUT)
            secure = kwargs.get('secure', True)
            strict = kwargs.get('strict', True)
            cert = kwargs.get('cert', None)
            cert_key = kwargs.get('cert_key', None)
            thread_local = kwargs.get('thread_local', threading.local())
            ldap_server = kwargs.get('remote_server', None)
            if not ldap_server:
                ldap_server = kwargs.get('ldap_server', None)
            if not self._context:
                self._context = ApiContext()
                self.__create_context(
                        self._context,
                        kwargs['hostname'],
                        username=kwargs['username'],
                        password=kwargs['password'],
                        tenant=tenant,
                        timeout=timeout,
                        secure=secure,
                        version=self._version,
                        strict=strict,
                        cert=cert,
                        cert_key=cert_key,
                        thread_local=thread_local,
                        ldap_server=ldap_server)
            return self._context

        @context.setter
        def context(self, value):
            self._context = value

        # We really don't want this overridden.  It messes with
        # initialization too much, thus the name-mangle
        def __create_context(self, context, hostname, username=None,
                             password=None, tenant=None, timeout=None,
                             secure=True, version=DEFAULT_API_VERSION,
                             strict=True, cert=None, cert_key=None,
                             thread_local=threading.local(),
                             remote_server=None):
            """
            Creates the context object
            This will be attached as a private attribute to all entities
            and endpoints returned by this API.

            Note that this is responsible for creating a connection object,
            which is an attribute of the context object.
            """
            context.version = version

            context.hostname = hostname
            context.username = username
            context.password = password
            context.tenant = tenant

            context.timeout = timeout
            context.secure = secure
            context.strict = strict
            context.cert = cert
            context.cert_key = cert_key

            context.connection = self._create_connection(context)
            context.thread_local = thread_local
            context.remote_server = remote_server

        def _create_connection(self, context):
            """
            Creates the API connection object used to communicate over REST
            """
            return ApiConnection(context)

    return _DateraBaseApi


class RootEp(_Endpoint):
    """
    Top-level endoint, the starting point for all API requests
    """
    _name = ""

    def __init__(self, *args):
        super(RootEp, self).__init__(*args)


class DateraApi(_api_getter(RootEp)):

    _version = 'v2'

    def __init__(self, *args, **kwargs):
        super(DateraApi, self).__init__(*args, **kwargs)


class DateraApi21(_api_getter(RootEp)):

    _version = 'v2.1'

    def __init__(self, *args, **kwargs):
        super(DateraApi21, self).__init__(*args, **kwargs)


class DateraApi22(_api_getter(RootEp)):

    _version = 'v2.2'

    def __init__(self, *args, **kwargs):
        super(DateraApi22, self).__init__(*args, **kwargs)
