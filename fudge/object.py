import os
import zlib

from collections import namedtuple

from fudge.utils import get_hash, get_repository_path, makedirs, read_file, write_file


Object = namedtuple('Object', ['type', 'size', 'contents'])


def get_object_path(digest, mkdir=False):
    basedir = get_repository_path()
    dirname, filename = digest[:2], digest[2:]

    dirpath = os.path.join(basedir, 'objects', dirname)
    if mkdir:
        makedirs(dirpath)

    return os.path.join(dirpath, filename)


def find_object_path(digest):
    if len(digest) < 4:
        raise Exception('fudge: invalid object name {}'.format(digest))

    basedir = get_repository_path()
    dirname, filepart = digest[:2], digest[2:]

    dirpath = os.path.join(basedir, 'objects', dirname)
    for filename in os.listdir(dirpath):
        if filename.startswith(filepart):
            return os.path.join(dirpath, filename)

    return None


def store_object(data):
    """Store an object in the object store."""
    if isinstance(data, str):
        data = bytes(data, 'utf-8')

    digest = get_hash(data)
    path = get_object_path(digest, mkdir=True)

    compressed = zlib.compress(data)
    write_file(path, compressed)


def load_object(digest):
    """Load an object from the object store."""
    path = find_object_path(digest)
    if not path:
        raise Exception('fudge: invalid object name {}'.format(digest))

    data = read_file(path)
    data = zlib.decompress(data)
    data = str(data, 'utf-8')

    header, contents = data.split('\0', 1)
    type_, size = header.split()
    return Object(type_, size, contents)
