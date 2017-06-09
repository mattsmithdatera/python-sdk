"""
Handles logging setup

Set the DSDK_LOG_CFG environment variable to set a custom path to a JSON
logging config file

Set the DSDK_LOG_STDOUT environment variable to a level (eg: debug, info) to
also send logging to STDOUT at the specified logging level
"""
import json
import logging
import logging.config
import os
import sys

from .constants import PYTHON_2_7_0_HEXVERSION


DEFAULT_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'logging.json')


def get_log(name):
    import logging
    log = logging.getLogger(name)
    if sys.hexversion >= PYTHON_2_7_0_HEXVERSION:
        if not log.handlers:
            log.addHandler(logging.NullHandler())
    return log


def setup_logging():
    path = os.getenv('DSDK_LOG_CFG', DEFAULT_LOG)
    with open(path) as f:
        j = json.load(f)
        logging.config.dictConfig(j)
    stdout = os.getenv('DSDK_LOG_STDOUT', None)
    if stdout:
        add_stdout(stdout)


def add_stdout(level):
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper()))
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(getattr(logging, level.upper()))
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)
