import binascii
import os
import sys

from fudge.index import Entry, ObjectType, read_index, write_index
from fudge.object import load_object, store_object
from fudge.utils import get_hash, get_repository_path, makedirs, read_file, write_file


def init():
    """Create an empty Git repository or reinitialize an existing one."""
    basedir = get_repository_path()
    subdirs = ['objects', 'refs/heads']

    reinit = os.path.exists(basedir)

    for subdir in subdirs:
        path = os.path.join(basedir, subdir)
        makedirs(path)

    path = os.path.join(basedir, 'HEAD')
    if not os.path.exists(path):
        write_file(path, 'ref: refs/heads/master\n', mode='w')

    if reinit:
        print('Reinitialized existing Git repository in {}'.format(basedir))
    else:
        print('Initialized empty Git repository in {}'.format(basedir))


def hash_object(path=None, stdin=False, write=False):
    """Compute an object ID and optionally creates a blob from a file."""
    if path:
        data = read_file(path, mode='r')
    elif stdin:
        data = sys.stdin.read()
    else:
        sys.exit(0)

    obj = 'blob {}\0{}'.format(len(data), data)
    digest = get_hash(obj)
    print(digest)

    if write:
        store_object(obj)


def cat_file(digest, show_type=False, show_size=False, show_contents=False):
    """Provide content, type or size information for repository objects."""
    obj = load_object(digest)

    if show_type:
        print(obj.type)
    elif show_size:
        print(obj.size)
    elif show_contents:
        print(obj.contents, end='')


def ls_files(stage=False):
    """Show information about files in the index."""
    index = read_index()
    for entry in index.entries:
        if stage:
            print(entry.perms, entry.checksum, entry.path)
        else:
            print(entry.path)


def update_index(path=None, add=False, cacheinfo=None):
    """Register file contents in the working tree to the index."""
    if path:
        data = read_file(path)
        digest = get_hash(data)
        mode = os.stat(path).st_mode
        mode = '{:o}'.format(mode)
    elif cacheinfo:
        info = cacheinfo.split(',')
        if len(info) != 3:
            print('fudge: `cacheinfo` expects <mode>,<sha1>,<path>')
            sys.exit(1)

        mode, digest, path = info
        if len(digest) != 40:
            print('fudge: invalid object name {}'.format(digest))
            sys.exit(1)
    else:
        sys.exit(0)

    index = read_index()
    if add:
        entry = Entry(
            ctime_s=0, ctime_n=0, mtime_s=0, mtime_n=0, dev=0, ino=0,
            object_type=ObjectType.REGULAR_FILE, perms=mode,
            uid=0, gid=0, size=0, checksum=digest, path=path
        )
        index.add(entry)
        write_index(index)


def write_tree():
    """Create a tree object from the current index."""
    index = read_index()
    obj = b''
    for entry in index.entries:
        line = '{} {}\0'.format(entry.perms, entry.path)
        checksum = binascii.unhexlify(entry.checksum)
        obj += bytes(line, 'utf-8') + checksum
    header = 'tree {}\0'.format(len(obj))
    obj = bytes(header, 'utf-8') + obj

    digest = get_hash(obj)
    print(digest)

    store_object(obj)


def symbolic_ref(name, ref=None, short=False):
    """Read, modify and delete symbolic refs."""
    basedir = get_repository_path()

    # Prevent directory traversal
    path = os.path.abspath(os.path.join(basedir, name))
    if not path.startswith(basedir):
        print('fudge: invalid name')
        sys.exit(1)

    if ref:
        if name == 'HEAD' and not ref.startswith('refs/'):
            print('fudge: refusing to point HEAD outside of refs/')
            sys.exit(1)

        write_file(path, 'ref: {}\n'.format(ref), mode='w')
    else:
        if not os.path.exists(path):
            print('fudge: ref file does not exist')
            sys.exit(1)

        data = read_file(path, mode='r').rstrip('\n')

        lines = data.split('\n')
        if len(lines) > 1:
            print('fudge: invalid ref file')
            sys.exit(1)

        parts = data.split(' ')
        if len(parts) != 2 and parts[0] != 'ref:':
            print('fudge: invalid ref file')
            sys.exit(1)

        ref = parts[1]
        if short:
            short_ref = ref.split('/')[-1]
            print(short_ref)
        else:
            print(ref)
