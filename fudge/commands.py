import hashlib
import os
import sys
import zlib

from fudge.index import Entry, ObjectType, read_index, write_index
from fudge.utils.path import get_repository_path, makedirs


def init():
    """Create an empty Git repository or reinitialize an existing one."""
    basedir = get_repository_path()
    subdirs = ['objects']

    reinit = os.path.exists(basedir)

    for subdir in subdirs:
        path = os.path.join(basedir, subdir)
        makedirs(path)

    if reinit:
        print('Reinitialized existing Git repository in {}'.format(basedir))
    else:
        print('Initialized empty Git repository in {}'.format(basedir))


def hash_object(path=None, stdin=False, write=False):
    """Compute an object ID and optionally creates a blob from a file."""
    data = None
    if path:
        with open(path, 'r') as f:
            data = f.read()
    elif stdin:
        data = sys.stdin.read()

    if not data:
        return

    blob = 'blob {}\0{}'.format(len(data), data)
    blob = bytes(blob, 'utf-8')

    digest = hashlib.sha1(blob).hexdigest()
    print(digest)

    if write:
        basedir = get_repository_path()
        dirname, filename = digest[:2], digest[2:]

        dirpath = os.path.join(basedir, 'objects', dirname)
        makedirs(dirpath)

        filepath = os.path.join(dirpath, filename)
        compressed = zlib.compress(blob)
        with open(filepath, 'wb') as f:
            f.write(compressed)


def cat_file(digest, show_type=False, show_size=False, show_contents=False):
    """Provide content, type or size information for repository objects."""
    if len(digest) != 40:
        print('fudge: invalid object name {}'.format(digest))
        sys.exit(1)

    basedir = get_repository_path()
    dirname, filename = digest[:2], digest[2:]
    path = os.path.join(basedir, 'objects', dirname, filename)
    if not os.path.exists(path):
        print('fudge: invalid object name {}'.format(digest))
        sys.exit(1)

    with open(path, 'rb') as f:
        data = f.read()
    data = zlib.decompress(data)
    data = str(data, 'utf-8')

    header, contents = data.split('\0', 1)
    type, size = header.split()

    if show_type:
        print(type)
    elif show_size:
        print(size)
    elif show_contents:
        print(contents, end='')


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
        with open(path, 'rb') as f:
            data = f.read()
        digest = hashlib.sha1(data).hexdigest()

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
        return

    index = read_index()
    if add:
        entry = Entry(
            ctime_s=0, ctime_n=0, mtime_s=0, mtime_n=0, dev=0, ino=0,
            object_type=ObjectType.REGULAR_FILE, perms=mode,
            uid=0, gid=0, size=0, checksum=digest, path=path
        )
        index.add(entry)
        write_index(index)
