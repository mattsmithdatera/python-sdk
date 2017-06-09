"""
Provides exceptions classes
"""
import json

from .logging import get_log

LOG = get_log(__name__)

__copyright__ = "Copyright 2017, Datera, Inc."


class ApiError(Exception):
    """ This is the base class for exceptions raised by the API """
    pass


###############################################################################


class ApiConnectionError(ApiError):
    """ Error trying to communicate with the server """
    pass


class ApiTimeoutError(ApiConnectionError):
    """ Timeout waiting for a response """
    pass


###############################################################################


class _ApiResponseError(ApiError):
    """
    This is the base class for exceptions raised due to an error returned
    by the REST server.

    The JSON response payload is made available as exception attributes
    """
    message = None
    code = None
    http = None
    name = None

    def __init__(self, msg, resp_data=None):
        super(_ApiResponseError, self).__init__(msg)
        self.msg = msg
        self.resp_data = resp_data or '{}'
        js = {}
        try:
            js = json.loads(self.resp_data)
        except ValueError:
            LOG.error("Invalid json payload from API response!")
        except TypeError as e:
            LOG.error("Object recieved from API response was unexpected type "
                      "error: {}, data: {}".format(e, self.resp_data))

        for attr in js.keys():
            # Intentionally overwrite exp.message since it's deprecated
            # str(exp) will use exp.args instead of exp.message
            if attr == 'message' or getattr(self, attr, None) is None:
                setattr(self, attr, js[attr])


class ApiAuthError(_ApiResponseError):
    """ Error due to wrong username/password """
    pass


class ApiInternalError(_ApiResponseError):
    """ HTTP 500 """
    pass


class ApiUnavailableError(_ApiResponseError):
    """
    HTTP 503, indicating that the REST server is having a transient error
    communicating with the backend.
    This is a temporary error, e.g. during a node failover or node install.
    """
    pass


class ApiInvalidRequestError(_ApiResponseError):
    """ Incorrect parameters or URL """
    pass


class ApiValidationFailedError(ApiInvalidRequestError):
    """ Request failed validation, see message attribute for reason """
    pass


class ApiNotFoundError(_ApiResponseError):
    """ HTTP 404 Not Found """
    pass


class ApiConflictError(_ApiResponseError):
    """ Edit conflict """
    pass
