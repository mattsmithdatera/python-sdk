"""
Provides hard-coded values used in this package.  No imports are allowed
since many other modules import this one
"""
__copyright__ = "Copyright 2017, Datera, Inc."

VERSION = "1.2.0"

VERSION_HISTORY = """
Version History:
    1.1.0 -- Initial Version
    1.1.1 -- Metadata Endpoint, Pep8 cleanup, Logging revamp
             Python 3 compatibility, Versioning and Version Headers,
    1.1.2 -- User, Event_system, Internal, Alerts Endpoints/Entities
    1.2.0 -- v2.2 support, API module refactor
"""

API_VERSIONS = ["v2", "v2.1", "v2.2"]

REST_PORT = 7717
REST_PORT_HTTPS = 7718

DEFAULT_HTTP_TIMEOUT = 300

PYTHON_2_7_0_HEXVERSION = 0x020700f0
PYTHON_2_7_9_HEXVERSION = 0x020709f0
PYTHON_3_0_0_HEXVERSION = 0x030000f0
