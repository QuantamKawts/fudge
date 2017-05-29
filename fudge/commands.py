import hashlib
import os
import sys
import zlib

from fudge.index import parse_index


def makedirs(path):
    """Create a path."""
    if not os.path.exists(path):
        os.makedirs(path)


def init(args):
    """Create an empty Git repository or reinitialize an existing one."""
    basedir = os.path.join(os.getcwd(), 'git/')
    subdirs = ['objects']

    reinit = os.path.exists(basedir)

    for subdir in subdirs:
        path = os.path.join(basedir, subdir)
        makedirs(path)

    if reinit:
        print('Reinitialized existing Git repository in {}'.format(basedir))
    else:
        print('Initialized empty Git repository in {}'.format(basedir))


def hash_object(args):
    """Compute an object ID and optionally creates a blob from a file."""
    data = None
    if args.file:
        with open(args.file, 'r') as f:
            data = f.read()
    elif args.stdin:
        data = sys.stdin.read()

    if not data:
        return

    blob = 'blob {}\0{}'.format(len(data), data)
    blob = bytes(blob, 'utf-8')

    digest = hashlib.sha1(blob).hexdigest()
    print(digest)

    if args.w:
        dirname, filename = digest[:2], digest[2:]

        dirpath = os.path.join(os.getcwd(), 'git', 'objects', dirname)
        makedirs(dirpath)

        filepath = os.path.join(dirpath, filename)
        compressed = zlib.compress(blob)
        with open(filepath, 'wb') as f:
            f.write(compressed)


def cat_file(args):
    """Provide content, type or size information for repository objects."""
    digest = args.object
    if len(digest) != 40:
        print('fudge: invalid object name {}'.format(digest))
        return

    dirname, filename = digest[:2], digest[2:]
    path = os.path.join(os.getcwd(), 'git', 'objects', dirname, filename)
    if not os.path.exists(path):
        print('fudge: invalid object name {}'.format(digest))
        return

    with open(path, 'rb') as f:
        data = f.read()
    data = zlib.decompress(data)
    data = str(data, 'utf-8')

    header, contents = data.split('\0', 1)
    type, size = header.split()

    if args.t:
        print(type)
    elif args.s:
        print(size)
    elif args.p:
        print(contents, end='')


def ls_files(args):
    """Show information about files in the index."""
    index = parse_index()
    for entry in index.entries:
        if args.stage:
            print(entry.perms, entry.checksum, entry.path)
        else:
            print(entry.path)


def update_index(args):
    """Register file contents in the working tree to the index."""
    pass
