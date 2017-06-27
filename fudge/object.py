import enum
import os
import zlib

from fudge.repository import get_repository_path
from fudge.utils import FudgeException, get_hash, makedirs, read_file, write_file


class Object(object):
    def __init__(self, type_, size, contents):
        self.type = type_
        self.size = size

        if isinstance(contents, str):
            contents = bytes(contents, 'utf-8')
        self.contents = contents

    @property
    def header(self):
        header = '{} {}\0'.format(self.type, self.size)
        return bytes(header, 'utf-8')

    @property
    def id(self):
        return get_hash(self.header + self.contents)


class ObjectType(enum.IntEnum):
    COMMIT = 1
    TREE = 2
    BLOB = 3
    TAG = 4
    DELTA_OFFSET = 6
    DELTA_BASE = 7

    @classmethod
    def exists(cls, value):
        return any(value == item.value for item in cls)

    @classmethod
    def to_name(cls, value):
        return ObjectType(value).name.lower()

    @classmethod
    def from_name(cls, value):
        value = value.upper()
        return ObjectType[value]


def get_object_path(object_id, mkdir=False):
    basedir = get_repository_path()
    dirname, filename = object_id[:2], object_id[2:]

    dirpath = os.path.join(basedir, 'objects', dirname)
    if mkdir:
        makedirs(dirpath)

    return os.path.join(dirpath, filename)


def find_object_path(object_id):
    if len(object_id) < 4:
        raise FudgeException('invalid object name {}'.format(object_id))

    basedir = get_repository_path()
    dirname, filepart = object_id[:2], object_id[2:]

    dirpath = os.path.join(basedir, 'objects', dirname)
    for filename in os.listdir(dirpath):
        if filename.startswith(filepart):
            return os.path.join(dirpath, filename)

    return None


def store_object(obj):
    """Store an object in the object store."""
    path = get_object_path(obj.id, mkdir=True)

    if not os.path.exists(path):
        compressed = zlib.compress(obj.header + obj.contents)
        write_file(path, compressed)


def load_object(object_id):
    """Load an object from the object store."""
    path = find_object_path(object_id)
    if not path:
        raise FudgeException('invalid object name {}'.format(object_id))

    data = read_file(path)
    data = zlib.decompress(data)

    header, contents = data.split(b'\0', 1)
    header = str(header, 'utf-8')
    type_, size = header.split()

    return Object(type_, size, contents)
