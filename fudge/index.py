import os
from collections import namedtuple

from sortedcontainers import SortedDict

from fudge.object import Object, get_object_path, load_object, store_object
from fudge.parsing.builder import Builder
from fudge.parsing.parser import Parser
from fudge.repository import get_repository_path, get_working_tree_path
from fudge.utils import FudgeException, get_hash, makedirs, read_file, stat, write_file


class Index(object):
    def __init__(self):
        self.entries = SortedDict()

    def __contains__(self, path):
        return path in self.entries

    def __iter__(self):
        for entry in self.entries.values():
            yield entry

    def __repr__(self):
        return 'Index(entries={!r})'.format(self.entries)

    def add(self, entry):
        """Add or update an index entry."""
        self.entries[entry.path] = entry

    def add_object(self, mode, object_id, path):
        # TODO: move elsewhere
        if mode == '160000':
            print('Skipping submodule {:.7} at {}'.format(object_id, path))
            return

        object_path = get_object_path(object_id)

        status = stat(object_path)
        # TODO: check the validity of mode
        status['perms'] = mode

        # TODO: handle symbolic links
        # TODO: normalize path
        entry = IndexEntry(object_id=object_id, object_type=ObjectType.REGULAR_FILE, path=path, **status)
        self.add(entry)

    def get(self, path):
        return self.entries.get(path)

    def remove(self, path):
        if path in self.entries:
            del self.entries[path]


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
        raise FudgeException('invalid index file magic')

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

    for entry in index:
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


def add_file_to_index(path):
    data = read_file(path)
    obj = Object('blob', len(data), data)
    store_object(obj)

    status = stat(path)
    status['perms'] = '100{:o}'.format(status['perms'])

    # TODO: handle symbolic links
    # TODO: normalize path
    entry = IndexEntry(object_type=ObjectType.REGULAR_FILE, object_id=obj.id, path=path, **status)

    index = read_index()
    index.add(entry)
    write_index(index)


def add_object_to_index(mode, object_id, path):
    index = read_index()
    index.add_object(mode, object_id, path)
    write_index(index)


def remove_from_index(path):
    index = read_index()
    if path not in index:
        raise FudgeException('path {} is not in the index'.format(path))

    index.remove(path)
    write_index(index)


def checkout_index():
    basedir = get_working_tree_path()

    index = read_index()
    for entry in index:
        path = os.path.join(basedir, entry.path)
        dirname = os.path.dirname(path)
        makedirs(dirname)

        if not os.path.exists(path):
            obj = load_object(entry.object_id)
            write_file(path, obj.contents)
