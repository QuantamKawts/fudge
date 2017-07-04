import os

from fudge.commit import read_commit
from fudge.index import read_index
from fudge.object import Object
from fudge.refs import read_ref
from fudge.repository import get_working_tree_path
from fudge.tree import build_tree_from_object, get_node, walk_tree
from fudge.utils import read_file


def get_gitignore_path():
    basedir = get_working_tree_path()
    return os.path.join(basedir, '.gitignore')


def parse_gitignore():
    """
    - Whitespace and trailing `/` are stripped.
    - Empty lines and lines starting with `#` are ignored.
    - Files and directories can be ignored by writing one name per line.
    - All files and directories with a specific extension can be ignored with the
      `*.<extension>` syntax.
    """
    ignored = set(['.fudge', '.git'])
    extensions = set()

    path = get_gitignore_path()
    if not os.path.exists(path):
        return ignored

    with open(path, 'r') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip().rstrip('/')
        if not line or line.startswith('#'):
            continue

        if line.startswith('*.'):
            extension = line.lstrip('*.')
            extensions.add(extension)

        ignored.add(line)

    return ignored, extensions


def walk_working_tree():
    ignored, extensions = parse_gitignore()

    def keep(name):
        extension = name.split('.')[-1]
        return name not in ignored and extension not in extensions

    basedir = get_working_tree_path()
    for dirpath, dirnames, filenames in os.walk(basedir):
        dirnames[:] = [d for d in dirnames if keep(d)]
        filenames[:] = [f for f in filenames if keep(f)]

        for filename in filenames:
            fullpath = os.path.join(dirpath, filename)
            path = os.path.relpath(fullpath, basedir)

            yield path


def compute_staged():
    """
    Let H be the set of file paths in the HEAD commit.
    Let I be the set of file paths in the index.

    Staged: differences between the index and the HEAD commit.

    - New files (in I and not in H): I - H.
    - Deleted files (in H and not in I): H - I.
    - Modified files: H & I where the object IDs differ.
    """
    staged = []

    index = read_index()

    commit_id = read_ref('HEAD')
    commit = read_commit(commit_id)
    tree = build_tree_from_object(commit.tree)

    index_paths = set([entry.path for entry in index])
    head_paths = set([path for path, node in walk_tree(tree, recurse=True) if node.is_leaf])

    new_files = index_paths - head_paths
    staged.extend([('new file', path) for path in new_files])

    deleted = head_paths - index_paths
    staged.extend([('deleted', path) for path in deleted])

    similar = head_paths & index_paths
    for path in similar:
        entry = index.get(path)
        node = get_node(tree, path)

        if entry.object_id != node.object_id:
            staged.append(('modified', path))

    staged.sort(key=lambda entry: entry[1])
    return staged


def compute_changed_and_untracked():
    """
    Let I be the set of file paths in the index.
    Let W be the set of file paths in the working tree.

    Changed: differences between the working tree and the index.

    - Deleted files (in I and not in W): I - W.
    - Modified files: I & W where the object IDs differ.

    Untracked: files in the working tree that are not in the index.

    - Untracked Files (in W and not in I): W - I.
    """
    changed = []
    untracked = []

    index = read_index()

    index_paths = set([entry.path for entry in index])
    working_tree_paths = set(list(walk_working_tree()))

    deleted = index_paths - working_tree_paths
    changed.extend([('deleted', path) for path in deleted])

    similar = index_paths & working_tree_paths
    for path in similar:
        entry = index.get(path)

        contents = read_file(path)
        obj = Object('blob', len(contents), contents)

        if entry.object_id != obj.id:
            changed.append(('modified', path))

    changed.sort(key=lambda entry: entry[1])

    untracked = list(working_tree_paths - index_paths)
    untracked.sort()

    return changed, untracked


def status():
    staged = compute_staged()
    changed, untracked = compute_changed_and_untracked()
    return staged, changed, untracked
