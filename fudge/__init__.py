import argparse
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


def main():
    commands = {
        'init': init,
        'hash-object': hash_object,
        'cat-file': cat_file,
        'ls-files': ls_files,
        'update-index': update_index,
    }

    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest='command')

    subparsers.add_parser(
        'init', help='Create an empty Git repository or reinitialize an existing one')

    hash_object_subparser = subparsers.add_parser(
        'hash-object', help='Compute an object ID and optionally creates a blob from a file')
    hash_object_subparser.add_argument(
        '-w', action='store_true', help='Actually write the object into the object database')
    hash_object_subparser.add_argument(
        '--stdin',
        action='store_true',
        help='Read the object from standard input instead of from a file'
    )
    hash_object_subparser.add_argument('file', nargs='?')

    cat_file_subparser = subparsers.add_parser(
        'cat-file', help='Provide content, type or size information for repository objects')
    cat_file_subparser.add_argument('object')
    group = cat_file_subparser.add_mutually_exclusive_group(required=True)
    group.add_argument('-t', action='store_true', help="Show the object's type")
    group.add_argument('-s', action='store_true', help="Show the object's size")
    group.add_argument('-p', action='store_true', help="Pretty-print the object's content")

    ls_files_subparser = subparsers.add_parser(
        'ls-files', help='Show information about files in the index')
    ls_files_subparser.add_argument(
        '-s',
        '--stage',
        action='store_true',
        help="Show staged contents' mode bits, object ID and object name"
    )

    update_index_subparser = subparsers.add_parser(
        'update-index', help='Register file contents in the working tree to the index')
    update_index_subparser.add_argument(
        '--add', action='store_true', help='Add the specified file to the index')
    update_index_subparser.add_argument(
        '--cacheinfo',
        metavar='<mode>,<object>,<path>',
        help='Directly insert the specified info into the index'
    )
    update_index_subparser.add_argument('file', nargs='?')

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command in commands:
        commands[args.command](args)
