import io
import os


DATA = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'data')


def load_asset(name):
    n = os.path.join(DATA, name)
    with io.open(n) as f:
        return f.read().encode('utf-8')
