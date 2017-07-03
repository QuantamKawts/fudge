import os
import sys

from fudge.commit import build_commit, iter_commits, parse_commit, write_commit
from fudge.index import (add_file_to_index, add_object_to_index, checkout_index, read_index,
                         remove_from_index)
from fudge.object import Object, load_object, store_object
from fudge.pack import parse_pack
from fudge.protocol import get_repository_name, upload_pack
from fudge.refs import write_ref, read_symbolic_ref, write_symbolic_ref
from fudge.repository import create_repository
from fudge.tree import build_tree_from_object, print_tree, read_tree, write_tree
from fudge.utils import read_file


def cmd_add(path=None):
    cmd_update_index(path=path, add=True)


def cmd_cat_file(object_id, show_type=False, show_size=False, show_contents=False):
    """Provide content, type or size information for repository objects."""
    obj = load_object(object_id)

    if show_type:
        print(obj.type)
    elif show_size:
        print(obj.size)
    elif show_contents:
        if obj.type == 'tree':
            cmd_ls_tree(object_id)
        else:
            contents = str(obj.contents, 'utf-8')
            print(contents, end='')


def cmd_checkout_index():
    checkout_index()


def cmd_clone(repo_url, repo_name=None):
    if not repo_name:
        repo_name = get_repository_name(repo_url)

    if os.path.exists(repo_name):
        print("destination path '{}' already exists".format(repo_name))
        sys.exit(1)

    print("Cloning into '{}'".format(repo_name))
    create_repository(repo_name)
    os.chdir(repo_name)

    print('Discovering refs and downloading a pack file')
    pack, head_object_id = upload_pack(repo_url)

    print('Parsing the pack file')
    objects = parse_pack(pack)

    for i, obj in enumerate(objects):
        print('\rWriting objects to disk ({}/{})'.format(i+1, len(objects)), end='')
        store_object(obj)
    print()

    print('Setting HEAD to {:.7}'.format(head_object_id))
    write_ref('HEAD', head_object_id)

    print('Checking out {:.7}'.format(head_object_id))
    obj = load_object(head_object_id)
    commit = parse_commit(obj)
    read_tree(commit.tree)
    checkout_index()


def cmd_commit(message=None):
    if not message:
        print('fudge: empty commit message')
        sys.exit(1)

    commit_id = write_commit(message)
    ref = read_symbolic_ref(short=True)

    short_message = message.split('\n', 1)[0]
    print('[{} {:.7}] {}'.format(ref, commit_id, short_message))


def cmd_commit_tree(tree, parent=None, message=None):
    parents = []
    if parent:
        parents = [parent]

    if not message:
        message = sys.stdin.read()

    commit = build_commit(tree, parents, message)
    store_object(commit)
    print(commit.id)


def cmd_hash_object(path=None, stdin=False, write=False):
    """Compute an object ID and optionally creates a blob from a file."""
    if path:
        data = read_file(path, mode='r')
    elif stdin:
        data = sys.stdin.read()
    else:
        sys.exit(0)

    obj = Object('blob', len(data), data)
    print(obj.id)

    if write:
        store_object(obj)


def cmd_init(path=None):
    """Create an empty Git repository or reinitialize an existing one."""
    fullpath, reinit = create_repository(path)

    if reinit:
        print('Reinitialized existing Git repository in {}'.format(fullpath))
    else:
        print('Initialized empty Git repository in {}'.format(fullpath))


def cmd_ls_files(stage=False):
    """Show information about files in the index."""
    index = read_index()
    for entry in index:
        if stage:
            print(entry.perms, entry.object_id, entry.path)
        else:
            print(entry.path)


def cmd_ls_tree(object_id, recurse=False):
    """List the contents of a tree object."""
    tree = build_tree_from_object(object_id)
    print_tree(tree, recurse)


def cmd_log(oneline):
    for commit in iter_commits():
        if oneline:
            short_message = commit.message.split('\n')[0]
            print('{:.7} {}'.format(commit.id, short_message))
        else:
            print('commit {}'.format(commit.id))
            print('Author: {} <{}>'.format(commit.author.name, commit.author.email))
            print('Date:   {}\n'.format(commit.author.datetime))
            print('{}\n'.format(commit.message))


def cmd_read_tree(tree):
    read_tree(tree)


def cmd_rm(path):
    """Remove a file from the index."""
    cmd_update_index(path, remove=True)
    print("rm '{}'".format(path))


def cmd_symbolic_ref(ref=None, short=False):
    """Read and modify the HEAD symbolic ref."""
    if ref:
        write_symbolic_ref(ref)
    else:
        ref = read_symbolic_ref(short=short)
        print(ref)


def cmd_update_index(path=None, add=False, remove=False, cacheinfo=None):
    """Register file contents in the working tree to the index."""
    if path:
        if add:
            add_file_to_index(path)
        elif remove:
            remove_from_index(path)
    elif cacheinfo:
        info = cacheinfo.split(',')
        if len(info) != 3:
            print('fudge: `cacheinfo` expects <mode>,<object>,<path>')
            sys.exit(1)

        mode, object_id, path = info
        if len(object_id) != 40:
            print('fudge: invalid object name {}'.format(object_id))
            sys.exit(1)

        if not add:
            print('fudge: missing --add option')
            sys.exit(1)

        add_object_to_index(mode, object_id, path)


def cmd_update_ref(ref, object_id):
    """Update the object name stored in a ref safely."""
    write_ref(ref, object_id)


def cmd_write_tree():
    """Create a tree object from the current index."""
    tree_id = write_tree()
    print(tree_id)
