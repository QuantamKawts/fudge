import os

from collections import namedtuple

from fudge.object import Object, get_object_path, store_object
from fudge.parsing.builder import Builder
from fudge.parsing.parser import Parser
from fudge.repository import get_repository_path
from fudge.utils import FudgeException, get_hash, read_file, stat, write_file


class Index(object):
    def __init__(self):
        self.entries = []

    def add(self, entry):
        self.entries.append(entry)
        self.entries.sort(key=lambda entry: entry.path)

    def __repr__(self):
        return 'Index(entries={!r})'.format(self.entries)


IndexEntry = namedtuple('IndexEntry', [
    'ctime_s', 'ctime_n', 'mtime_s', 'mtime_n', 'dev', 'ino', 'object_type',
    'perms', 'uid', 'gid', 'size', 'object_id', 'path'
])


class ObjectType(object):
    REGULAR_FILE = 0b1000
    SYMBOLIC_LINK = 0b1010
    GITLINK = 0b1110


def get_index_path():
    basedir = get_repository_path()
    return os.path.join(basedir, 'index')


def read_index():
    """Read an index file."""
    path = get_index_path()
    if not os.path.exists(path):
        return Index()

    data = read_file(path)

    header_parser = Parser(data[:12])
    parser = Parser(data[12:])

    if header_parser.get(4) != b'DIRC':
        raise FudgeException('invalid index file')

    version = header_parser.get_u4()
    if version != 2:
        raise FudgeException('unsupported index file version: {}'.format(version))

    index = Index()

    num_index_entries = header_parser.get_u4()

    for _ in range(num_index_entries):
        ctime_s = parser.get_u4()
        ctime_n = parser.get_u4()
        mtime_s = parser.get_u4()
        mtime_n = parser.get_u4()
        dev = parser.get_u4()
        ino = parser.get_u4()

        mode = parser.get_u4()
        object_type = (mode >> 12) & 0xf
        if object_type not in (ObjectType.REGULAR_FILE, ObjectType.SYMBOLIC_LINK, ObjectType.GITLINK):
            raise FudgeException('invalid object type: 0b{:b}'.format(object_type))

        perms = mode & 0x1ff
        if object_type == ObjectType.REGULAR_FILE and perms not in (0o755, 0o644):
            raise FudgeException('invalid permissions')
        elif object_type in (ObjectType.SYMBOLIC_LINK, ObjectType.GITLINK) and perms != 0:
            raise FudgeException('invalid permissions')

        perms = '100{:o}'.format(perms)

        uid = parser.get_u4()
        gid = parser.get_u4()
        size = parser.get_u4()
        object_id = parser.get_sha1()

        flags = parser.get_u2()
        assume_valid = (flags >> 15) & 0b1
        extended = (flags >> 14) & 0b1
        if extended != 0:
            raise FudgeException('invalid extended flag')

        stage = (flags >> 12) & 0b11
        name_length = flags & 0xfff

        path = parser.get_utf8()

        entry = IndexEntry(
            ctime_s, ctime_n, mtime_s, mtime_n, dev, ino, object_type, perms,
            uid, gid, size, object_id, path
        )
        index.add(entry)

    # Skip extensions
    parser.offset = len(parser.data) - 20
    index_checksum = parser.get_sha1()

    data = header_parser.data + parser.data[:parser.offset-20]
    data_checksum = get_hash(data)
    if index_checksum != data_checksum:
        raise FudgeException('bad index file checksum')

    return index


def write_index(index):
    """Write an index file."""
    header_builder = Builder()
    header_builder.set(b'DIRC')
    header_builder.set_u4(2)
    header_builder.set_u4(len(index.entries))

    builder = Builder()

    for entry in index.entries:
        builder.set_u4(entry.ctime_s)
        builder.set_u4(entry.ctime_n)
        builder.set_u4(entry.mtime_s)
        builder.set_u4(entry.mtime_n)
        builder.set_u4(entry.dev)
        builder.set_u4(entry.ino)

        perms = int(entry.perms[3:], 8)
        mode = (entry.object_type << 12) | perms
        builder.set_u4(mode)

        builder.set_u4(entry.uid)
        builder.set_u4(entry.gid)
        builder.set_u4(entry.size)
        builder.set_sha1(entry.object_id)

        # TODO: do not ignore the assume valid, extended and stage flags
        flags = len(entry.path)
        builder.set_u2(flags)

        builder.set_utf8(entry.path)

    data = header_builder.data + builder.data

    checksum = get_hash(data)
    builder.set_sha1(checksum)

    data = header_builder.data + builder.data

    path = get_index_path()
    write_file(path, data)


def add_to_index(entry):
    index = read_index()
    index.add(entry)
    write_index(index)


def add_file_to_index(path):
    data = read_file(path)
    obj = Object('blob', len(data), data)
    store_object(obj)

    status = stat(path)
    status['perms'] = '100{:o}'.format(status['perms'])

    # TODO: handle symbolic links
    entry = IndexEntry(object_type=ObjectType.REGULAR_FILE, object_id=obj.id, path=path, **status)
    add_to_index(entry)


def add_object_to_index(mode, object_id, path):
    object_path = get_object_path(object_id)
    status = stat(object_path)
    # TODO: check the validity of mode
    status['perms'] = mode

    # TODO: handle symbolic links
    entry = IndexEntry(object_type=ObjectType.REGULAR_FILE, object_id=object_id, path=path, **status)
    add_to_index(entry)
