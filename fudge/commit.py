import time

from fudge.config import get_config_value
from fudge.object import Object, load_object, store_object
from fudge.tree import build_tree
from fudge.refs import read_ref, write_ref
from fudge.utils import FudgeException


def build_commit(tree, parents, message):
    obj = load_object(tree)
    if obj.type != 'tree':
        raise FudgeException('the specified object is not a tree')

    contents = 'tree {}\n'.format(obj.id)

    for parent in parents:
        obj = load_object(parent)
        if obj.type != 'commit':
            raise FudgeException('one of the specified parents is not a commit')

        contents += 'parent {}\n'.format(obj.id)

    name = get_config_value('user', 'name')
    email = get_config_value('user', 'email')
    if not name or not email:
        raise FudgeException('name or email not set')

    timestamp = int(time.time())
    offset = time.strftime('%z')

    contents += 'author {} <{}> {} {}\n'.format(name, email, timestamp, offset)
    contents += 'committer {} <{}> {} {}\n\n'.format(name, email, timestamp, offset)

    message = message.rstrip()

    contents += '{}\n'.format(message)

    return Object('commit', len(contents), contents)


def write_commit(message):
    tree = build_tree()
    store_object(tree)

    parent = read_ref('HEAD')

    commit = build_commit(tree.id, [parent], message)
    store_object(commit)

    write_ref('HEAD', commit.id)
