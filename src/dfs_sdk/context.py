"""
Provides the ApiContext class
"""
__copyright__ = "Copyright 2017, Datera, Inc."


class ApiContext(object):
    """
    This object is created by the top level API object, and is passed in
    to all endpoints and entities.
    """

    def __init__(self):
        self.connection = None

        self.hostname = None
        self.username = None
        self.password = None
        self.tenant = None

        self.timeout = None
        self.secure = None
        self.version = None

        self._reader = None
        self.strict = True

    @property
    def reader(self):
        if not self._reader:
            self.connection.login(
                name=self.username, password=self.password)
            self._reader = self.connection.reader
        return self._reader
