import io
import json
import itertools
import os


CURR = os.getcwd()
TESTS = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(TESTS, 'data')


def update_side_effect(mock, *args):
    mock.side_effect = itertools.chain(mock.side_effect, args)


def load_asset(name):
    n = os.path.join(DATA, name)
    with io.open(n) as f:
        return json.loads(f.read())
