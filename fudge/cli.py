import argparse
import sys

from fudge.commands import (cat_file, hash_object, init, ls_files, symbolic_ref, update_index,
                            write_tree)


def cli():
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

    symbolic_ref_subparser = subparsers.add_parser(
        'symbolic-ref', help='Read, modify and delete symbolic refs')
    symbolic_ref_subparser.add_argument('name')
    symbolic_ref_subparser.add_argument('ref', nargs='?')
    symbolic_ref_subparser.add_argument(
        '--short', action='store_true', help='Shorten the ref output')

    update_index_subparser = subparsers.add_parser(
        'update-index', help='Register file contents in the working tree to the index')
    update_index_subparser.add_argument(
        '--add', action='store_true', help='Add the specified file to the index')
    update_index_subparser.add_argument(
        '--cacheinfo',
        metavar='<mode>,<sha1>,<path>',
        help='Directly insert the specified info into the index'
    )
    update_index_subparser.add_argument('file', nargs='?')

    subparsers.add_parser('write-tree', help='Create a tree object from the current index')

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == 'cat-file':
        cat_file(args.object, args.t, args.s, args.p)
    elif args.command == 'hash-object':
        hash_object(args.file, args.stdin, args.w)
    elif args.command == 'init':
        init()
    elif args.command == 'ls-files':
        ls_files(args.stage)
    elif args.command == 'symbolic-ref':
        symbolic_ref(args.name, args.ref, args.short)
    elif args.command == 'update-index':
        update_index(args.file, args.add, args.cacheinfo)
    elif args.command == 'write-tree':
        write_tree()
