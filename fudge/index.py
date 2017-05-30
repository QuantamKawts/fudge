import hashlib
import os

from collections import namedtuple

from fudge.utils.builder import Builder
from fudge.utils.parser import Parser
from fudge.utils.path import get_repository_path


class Index(object):
    def __init__(self, version):
        self.version = version

        self.checksum = None
        self.entries = []

    def add(self, entry):
        self.entries.append(entry)
        self.entries.sort(key=lambda entry: entry.path)

    def __repr__(self):
        return 'Index(entries={!r})'.format(self.entries)


Entry = namedtuple('Entry', [
    'ctime_s', 'ctime_n', 'mtime_s', 'mtime_n', 'dev', 'ino', 'object_type',
    'perms', 'uid', 'gid', 'size', 'checksum', 'path'
])


class ObjectType(object):
    REGULAR_FILE = 0b1000
    SYMBOLIC_LINK = 0b1010
    GITLINK = 0b1110


def read_index():
    """Read an index file."""
    basedir = get_repository_path()
    path = os.path.join(basedir, 'index')
    if not os.path.exists(path):
        return Index(2)

    with open(path, 'rb') as f:
        data = f.read()

    header_parser = Parser(data[:12])
    parser = Parser(data[12:])

    if header_parser.get(4) != b'DIRC':
        raise Exception('fudge: invalid index file')

    version = header_parser.get_u4()
    if version != 2:
        raise Exception('fudge: unsupported index file version: {}'.format(version))

    index = Index(version)

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
            raise Exception('fudge: invalid object type: 0b{:b}'.format(object_type))

        perms = mode & 0x1ff
        if object_type == ObjectType.REGULAR_FILE and perms not in (0o755, 0o644):
            raise Exception('fudge: invalid permissions')
        elif object_type in (ObjectType.SYMBOLIC_LINK, ObjectType.GITLINK) and perms != 0:
            raise Exception('fudge: invalid permissions')

        perms = '100{:o}'.format(perms)

        uid = parser.get_u4()
        gid = parser.get_u4()
        size = parser.get_u4()
        checksum = parser.get_sha1()

        flags = parser.get_u2()
        assume_valid = (flags >> 15) & 0b1
        extended = (flags >> 14) & 0b1
        if extended != 0:
            raise Exception('fudge: invalid extended flag')

        stage = (flags >> 12) & 0b11
        name_length = flags & 0xfff

        path = parser.get_utf8()

        entry = Entry(
            ctime_s, ctime_n, mtime_s, mtime_n, dev, ino, object_type, perms,
            uid, gid, size, checksum, path
        )
        index.add(entry)

    # Skip extensions
    parser.offset = len(parser.data) - 20
    checksum = parser.get_sha1()
    index.checksum = checksum

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
        builder.set_sha1(entry.checksum)

        # TODO: do not ignore the assume valid, extended and stage flags
        flags = len(entry.path)
        builder.set_u2(flags)

        builder.set_utf8(entry.path)

    data = header_builder.data + builder.data

    digest = hashlib.sha1(data).hexdigest()
    builder.set_sha1(digest)

    data = header_builder.data + builder.data

    basedir = get_repository_path()
    path = os.path.join(basedir, 'index')
    with open(path, 'wb') as f:
        f.write(data)
