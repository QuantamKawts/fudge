import hashlib
import os


class FudgeException(Exception):
    pass


def read_file(path, mode='rb'):
    with open(path, mode) as f:
        data = f.read()
    return data


def write_file(path, data, mode='wb'):
    with open(path, mode) as f:
        f.write(data)


def makedirs(path):
    """Create a path."""
    if not os.path.exists(path):
        os.makedirs(path)


def get_hash(data):
    if isinstance(data, str):
        data = bytes(data, 'utf-8')

    digest = hashlib.sha1(data).hexdigest()
    return digest


def get_repository_path():
    basedir = os.environ.get('FUDGE_DIR')
    if basedir:
        basedir = os.path.abspath(basedir)
    else:
        basedir = os.getcwd()
    return os.path.join(basedir, '.fudge')
