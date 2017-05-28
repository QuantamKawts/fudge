import argparse
import errno
import hashlib
import os
import sys
import zlib


def makedirs(path):
    """Create a path."""
    try:
        os.makedirs(path)
    except OSError as error:
        if error.errno != errno.EEXIST:
            raise error


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


def main():
    commands = {
        'init': init,
        'hash-object': hash_object,
        'cat-file': cat_file,
    }

    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest='command')

    subparsers.add_parser(
        'init',
        help='Create an empty Git repository or reinitialize an existing one'
    )

    hash_object_subparser = subparsers.add_parser(
        'hash-object', help='Compute an object ID and optionally creates a blob from a file')
    hash_object_subparser.add_argument(
        '-w',
        action='store_true',
        help='Actually write the object into the object database.'
    )
    hash_object_subparser.add_argument(
        '--stdin',
        action='store_true',
        help='Read the object from standard input instead of from a file.'
    )
    hash_object_subparser.add_argument('file', nargs='?')

    cat_file_subparser = subparsers.add_parser(
        'cat-file', help='Provide content, type or size information for repository objects')
    cat_file_subparser.add_argument('object')
    group = cat_file_subparser.add_mutually_exclusive_group(required=True)
    group.add_argument('-t', action='store_true', help="Show the object's type.")
    group.add_argument('-s', action='store_true', help="Show the object's size.")
    group.add_argument('-p', action='store_true', help="Pretty-print the object's content.")

    args = parser.parse_args()
    if args.command in commands:
        commands[args.command](args)
    else:
        print("fudge: {} is not a git command. See 'fudge --help'".format(args.command))


if __name__ == '__main__':
    main()
