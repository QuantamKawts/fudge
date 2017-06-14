import hashlib
import os
from string import hexdigits


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

    return hashlib.sha1(data).hexdigest()


def ishex(string):
    digits = set(hexdigits)
    return all(char in digits for char in string)


def issafe(string):
    blacklist = ['\0', '\n', '<', '>']
    edge_blacklist = [' ', '.', ',', ':', ';', '"', "'"]
    return not any(char in blacklist for char in string) \
        and not any(string.startswith(char) for char in edge_blacklist) \
        and not any(string.endswith(char) for char in edge_blacklist)
