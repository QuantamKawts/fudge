import argparse
import sys

from fudge.commands import (cmd_add, cmd_cat_file, cmd_checkout_index, cmd_clone, cmd_commit,
                            cmd_commit_tree, cmd_hash_object, cmd_init, cmd_ls_files, cmd_ls_tree,
                            cmd_log, cmd_read_tree, cmd_rm, cmd_status, cmd_symbolic_ref,
                            cmd_update_index, cmd_update_ref, cmd_write_tree)


def cli():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest='command')

    add_subparser = subparsers.add_parser(
        'add', help='Add file contents to the index')
    add_subparser.add_argument('path')

    cat_file_subparser = subparsers.add_parser(
        'cat-file', help='Provide content, type or size information for repository objects')
    cat_file_subparser.add_argument('object')
    group = cat_file_subparser.add_mutually_exclusive_group(required=True)
    group.add_argument('-t', action='store_true', help="Show the object's type")
    group.add_argument('-s', action='store_true', help="Show the object's size")
    group.add_argument('-p', action='store_true', help="Pretty-print the object's content")

    clone_subparser = subparsers.add_parser(
        'clone', help='Clone a repository into a new directory')
    clone_subparser.add_argument('repository')
    clone_subparser.add_argument('path', nargs='?')

    subparsers.add_parser('checkout-index', help='Copy files from the index to the working tree')

    commit_subparser = subparsers.add_parser(
        'commit', help='Record changes to the repository')
    commit_subparser.add_argument(
        '-m', metavar='message', nargs='?', help='The commit log message')

    commit_tree_subparser = subparsers.add_parser(
        'commit-tree', help='Create a new commit object')
    commit_tree_subparser.add_argument(
        '-p', metavar='parent', nargs='?', help='The id of a parent commit object')
    commit_tree_subparser.add_argument(
        '-m', metavar='message', nargs='?', help='The commit log message')
    commit_tree_subparser.add_argument('tree')

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

    init_subparser = subparsers.add_parser(
        'init', help='Create an empty Git repository or reinitialize an existing one')
    init_subparser.add_argument('path', nargs='?')

    ls_files_subparser = subparsers.add_parser(
        'ls-files', help='Show information about files in the index')
    ls_files_subparser.add_argument(
        '-s',
        '--stage',
        action='store_true',
        help="Show staged contents' mode bits, object ID and object name"
    )

    ls_tree_subparser = subparsers.add_parser(
        'ls-tree', help='List the contents of a tree object')
    ls_tree_subparser.add_argument('-r', action='store_true', help='Recurse into sub-trees')
    ls_tree_subparser.add_argument('tree')

    log_subparser = subparsers.add_parser('log', help='Show commit logs')
    log_subparser.add_argument('--oneline', action='store_true')

    read_tree_subparser = subparsers.add_parser(
        'read-tree', help='Read tree information into the index')
    read_tree_subparser.add_argument('tree')

    rm_subparser = subparsers.add_parser(
        'rm', help='Remove a file from the index')
    rm_subparser.add_argument('path')

    subparsers.add_parser(
        'status', help='Show the working tree status')

    symbolic_ref_subparser = subparsers.add_parser(
        'symbolic-ref', help='Read and modify the HEAD symbolic ref')
    symbolic_ref_subparser.add_argument('ref', nargs='?')
    symbolic_ref_subparser.add_argument(
        '--short', action='store_true', help='Shorten the ref output')

    update_index_subparser = subparsers.add_parser(
        'update-index', help='Register file contents in the working tree to the index')
    update_index_subparser.add_argument(
        '--add', action='store_true', help='Add the specified file to the index')
    update_index_subparser.add_argument(
        '--remove', action='store_true', help='Remove the specified file from the index')
    update_index_subparser.add_argument(
        '--cacheinfo',
        metavar='<mode>,<object>,<path>',
        help='Directly insert the specified info into the index'
    )
    update_index_subparser.add_argument('file', nargs='?')

    update_ref_subparser = subparsers.add_parser(
        'update-ref', help='Update the object name stored in a ref safely')
    update_ref_subparser.add_argument('ref')
    update_ref_subparser.add_argument('object')

    subparsers.add_parser('write-tree', help='Create a tree object from the current index')

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == 'add':
        cmd_add(args.path)
    elif args.command == 'cat-file':
        cmd_cat_file(args.object, args.t, args.s, args.p)
    elif args.command == 'checkout-index':
        cmd_checkout_index()
    elif args.command == 'clone':
        cmd_clone(args.repository, args.path)
    elif args.command == 'commit':
        cmd_commit(args.m)
    elif args.command == 'commit-tree':
        cmd_commit_tree(args.tree, args.p, args.m)
    elif args.command == 'hash-object':
        cmd_hash_object(args.file, args.stdin, args.w)
    elif args.command == 'init':
        cmd_init(args.path)
    elif args.command == 'ls-files':
        cmd_ls_files(args.stage)
    elif args.command == 'ls-tree':
        cmd_ls_tree(args.tree, args.r)
    elif args.command == 'log':
        cmd_log(args.oneline)
    elif args.command == 'read-tree':
        cmd_read_tree(args.tree)
    elif args.command == 'rm':
        cmd_rm(args.path)
    elif args.command == 'status':
        cmd_status()
    elif args.command == 'symbolic-ref':
        cmd_symbolic_ref(args.ref, args.short)
    elif args.command == 'update-index':
        cmd_update_index(args.file, args.add, args.remove, args.cacheinfo)
    elif args.command == 'update-ref':
        cmd_update_ref(args.ref, args.object)
    elif args.command == 'write-tree':
        cmd_write_tree()
