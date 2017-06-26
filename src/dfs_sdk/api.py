"""
Provides the DateraApi objects
"""
from .constants import DEFAULT_HTTP_TIMEOUT
from .connection import ApiConnection
from .context import ApiContext
from .types_v2 import RootEp as RootEp2
from .types_v2_1 import RootEp as RootEp21
from .types_v2_2 import RootEp as RootEp22

__copyright__ = "Copyright 2017, Datera, Inc."


DEFAULT_API_VERSION = "v2.1"


# Wrapper function to help deduplicate all the code we were getting with the
# different api versions with little to no difference in this class
def _api_getter(base):

    class Base(base):
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

            tenant = kwargs.get('tenant', None)
            timeout = kwargs.get('timeout', DEFAULT_HTTP_TIMEOUT)
            immediate_login = kwargs.get('immediate_login', True)
            secure = kwargs.get('secure', True)

            # Create the context object, common to all endpoints and entities:
            self._context = self._create_context(hostname,
                                                 username=username,
                                                 password=password,
                                                 tenant=tenant,
                                                 timeout=timeout,
                                                 secure=secure)

            if immediate_login:
                self._context.connection.login(
                    name=username, password=password)

            # Initialize sub-endpoints:
            super(Base, self).__init__(self._context, None)

        def _create_context(self, hostname, username=None, password=None,
                            tenant=None, timeout=None, secure=True,
                            version=DEFAULT_API_VERSION):
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
            return context

        def _create_connection(self, context):
            """
            Creates the API connection object used to communicate over REST
            """
            return ApiConnection(context)

    return Base


class DateraApi(_api_getter(RootEp2)):
    def __init__(self, *args, **kwargs):
        super(DateraApi, self).__init__(*args, **kwargs)


class DateraApi21(_api_getter(RootEp21)):
    def __init__(self, *args, **kwargs):
        super(DateraApi21, self).__init__(*args, **kwargs)


class DateraApi22(_api_getter(RootEp22)):
    def __init__(self, *args, **kwargs):
        super(DateraApi22, self).__init__(*args, **kwargs)
