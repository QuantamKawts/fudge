from collections import namedtuple
from datetime import datetime
import time

from fudge.config import get_config_value
from fudge.object import Object, load_object, store_object
from fudge.tree import build_tree
from fudge.refs import read_ref, write_ref
from fudge.utils import FudgeException


Commit = namedtuple('Commit', ['id', 'tree', 'parents', 'author', 'committer', 'message'])


class Author(object):
    def __init__(self, name, email, timestamp, offset):
        self.name = name
        self.email = email
        self.timestamp = float(timestamp)
        self.offset = offset

    @property
    def datetime(self):
        utc_datetime = datetime.utcfromtimestamp(self.timestamp)
        return '{} {}'.format(utc_datetime.strftime('%c'), self.offset)


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


def parse_commit(obj):
    if obj.type != 'commit':
        raise FudgeException('the specified object is not a commit')

    contents = str(obj.contents, 'utf-8')
    header, message = contents.split('\n\n', 1)
    message = message.rstrip('\n')
    lines = iter(header.split('\n'))

    tree_keyword, tree_id = next(lines).split()

    parents = []
    while True:
        line = next(lines).split()
        parent_keyword, parent_id = line[0:2]
        if parent_keyword != 'parent':
            break

        parents.append(parent_id)

    # FIXME: Git author names can contain spaces
    author_keyword, name, email, timestamp, offset = line
    email = email.lstrip('<').rstrip('>')
    author = Author(name, email, timestamp, offset)

    # FIXME: Git committer names can contain spaces
    committer_keyword, name, email, timestamp, offset = next(lines).split()
    email = email.lstrip('<').rstrip('>')
    committer = Author(name, email, timestamp, offset)

    return Commit(obj.id, tree_id, parents, author, committer, message)


def iter_commits():
    object_id = read_ref('HEAD')

    while True:
        obj = load_object(object_id)
        commit = parse_commit(obj)

        yield commit

        if not commit.parents:
            break

        object_id = commit.parents[0]
