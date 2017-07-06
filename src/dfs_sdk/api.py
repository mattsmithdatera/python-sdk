"""
Provides the DateraApi objects
"""
import io
import json
import os

from .constants import DEFAULT_HTTP_TIMEOUT
from .connection import ApiConnection
from .context import ApiContext
from .base import Endpoint as _Endpoint
from .schema.reader import get_reader

__copyright__ = "Copyright 2017, Datera, Inc."


DEFAULT_API_VERSION = "v2.1"
CACHED_SCHEMA = ".cached-schema"


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
            """
            if not hostname or not username or not password:
                raise ValueError(
                    "hostname, username, and password are required")

            # Create the context object, common to all endpoints and entities:
            reader = get_reader(self._version)
            kwargs['hostname'] = hostname
            kwargs['username'] = username
            kwargs['password'] = password
            kwargs['reader'] = reader
            self._kwargs = kwargs
            self._context = None

            immediate_login = kwargs.get('immediate_login', True)
            if immediate_login:
                self.login()

            # Initialize sub-endpoints:
            super(_DateraBaseApi, self).__init__(self._context, None)

        def login(self):
            kwargs = self._kwargs
            self.context.connection.login(
                name=kwargs['username'], password=kwargs['password'])

        @property
        def context(self):
            kwargs = self._kwargs
            tenant = kwargs.get('tenant', None)
            timeout = kwargs.get('timeout', DEFAULT_HTTP_TIMEOUT)
            secure = kwargs.get('secure', True)
            if not self._context:
                self._context = self._create_context(
                        kwargs['hostname'],
                        username=kwargs['username'],
                        password=kwargs['password'],
                        tenant=tenant,
                        timeout=timeout,
                        secure=secure,
                        version=self._version,
                        reader=kwargs['reader'])
            return self._context

        @context.setter
        def context(self, value):
            self._context = value

        def _get_schema(self, connection, version, endpoint):
            """
            Tries to access cached schema, if not available, pulls new schema
            from the remote box.
            """
            data = None
            if os.path.exists(CACHED_SCHEMA):
                with io.open(CACHED_SCHEMA, 'r') as f:
                    data = json.loads(f.read())
                    if version in data:
                        return data[version]
                    data[version] = connection.read_endpoint(endpoint)
            else:
                data = {version: connection.read_endpoint(endpoint)}
            with io.open(CACHED_SCHEMA, 'w+') as f:
                f.write(json.dumps(data))
            return data[version]

        def _create_context(self, hostname, username=None, password=None,
                            tenant=None, timeout=None, secure=True,
                            version=DEFAULT_API_VERSION, reader=None):
            """
            Creates the context object
            This will be attached as a private attribute to all entities
            and endpoints returned by this API.

            Note that this is responsible for creating a connection object,
            which is an attribute of the context object.
            """
            context = ApiContext()
            context.version = version

            context.hostname = hostname
            context.username = username
            context.password = password
            context.tenant = tenant

            context.timeout = timeout
            context.secure = secure

            context.connection = self._create_connection(context)

            schema = self._get_schema(
                context.connection, version, reader._endpoint)
            context.reader = reader(schema)

            return context

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
