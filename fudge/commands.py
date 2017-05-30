import hashlib
import os
import sys
import zlib

from fudge.index import read_index
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


def hash_object(path, stdin, write):
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


def cat_file(digest, show_type, show_size, show_contents):
    """Provide content, type or size information for repository objects."""
    if len(digest) != 40:
        print('fudge: invalid object name {}'.format(digest))
        return

    basedir = get_repository_path()
    dirname, filename = digest[:2], digest[2:]
    path = os.path.join(basedir, 'objects', dirname, filename)
    if not os.path.exists(path):
        print('fudge: invalid object name {}'.format(digest))
        return

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


def update_index():
    """Register file contents in the working tree to the index."""
    pass
