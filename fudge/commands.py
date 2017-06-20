import os
import sys

from fudge.commit import build_commit, iter_commits, write_commit
from fudge.index import Entry, ObjectType, read_index, write_index
from fudge.object import Object, load_object, store_object
from fudge.pack import parse_pack
from fudge.protocol import upload_pack
from fudge.refs import write_ref, read_symbolic_ref, write_symbolic_ref
from fudge.repository import create_repository, get_repository_path
from fudge.tree import build_tree, parse_tree
from fudge.utils import read_file


def cmd_cat_file(digest, show_type=False, show_size=False, show_contents=False):
    """Provide content, type or size information for repository objects."""
    obj = load_object(digest)

    if show_type:
        print(obj.type)
    elif show_size:
        print(obj.size)
    elif show_contents:
        if obj.type == 'tree':
            cmd_ls_tree(digest)
        else:
            contents = str(obj.contents, 'utf-8')
            print(contents, end='')


def cmd_clone(repository):
    print('Discovering refs and downloading a pack file')
    pack = upload_pack(repository)

    print('Parsing the pack file')
    objects = parse_pack(pack)

    print('Writing {} objects to disk'.format(len(objects)))
    for obj in objects:
        store_object(obj)


def cmd_commit(message=None):
    if not message:
        print('fudge: empty commit message')
        sys.exit(1)

    write_commit(message)


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


def cmd_init():
    """Create an empty Git repository or reinitialize an existing one."""
    basedir = get_repository_path()
    reinit = os.path.exists(basedir)

    create_repository()

    if reinit:
        print('Reinitialized existing Git repository in {}'.format(basedir))
    else:
        print('Initialized empty Git repository in {}'.format(basedir))


def cmd_ls_files(stage=False):
    """Show information about files in the index."""
    index = read_index()
    for entry in index.entries:
        if stage:
            print(entry.perms, entry.checksum, entry.path)
        else:
            print(entry.path)


def cmd_ls_tree(digest):
    """List the contents of a tree object."""
    obj = load_object(digest)

    tree = parse_tree(obj)
    for entry in tree.entries:
        obj = load_object(entry.checksum)
        print(entry.mode, obj.type, entry.checksum, entry.path)


def cmd_log(oneline):
    for commit in iter_commits():
        if oneline:
            short_id = commit.id[:7]
            short_message = commit.message.split('\n')[0]
            print('{} {}'.format(short_id, short_message))
        else:
            print('commit {}'.format(commit.id))
            print('Author: {} <{}>'.format(commit.author.name, commit.author.email))
            print('Date:   {}\n'.format(commit.author.datetime))
            print('{}\n'.format(commit.message))


def cmd_symbolic_ref(ref=None, short=False):
    """Read and modify the HEAD symbolic ref."""
    if ref:
        write_symbolic_ref(ref)
    else:
        ref = read_symbolic_ref()
        if short:
            short_ref = ref.split('/')[-1]
            print(short_ref)
        else:
            print(ref)


def cmd_update_index(path=None, add=False, cacheinfo=None):
    """Register file contents in the working tree to the index."""
    if path:
        data = read_file(path)

        obj = Object('blob', len(data), data)
        store_object(obj)

        digest = obj.id
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


def cmd_update_ref(ref, object_id):
    """Update the object name stored in a ref safely."""
    write_ref(ref, object_id)


def cmd_write_tree():
    """Create a tree object from the current index."""
    obj = build_tree()
    store_object(obj)
    print(obj.id)
