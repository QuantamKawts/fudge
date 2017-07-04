import datetime
import time
from collections import namedtuple

from fudge.config import get_config_value
from fudge.object import Object, load_object, store_object
from fudge.tree import write_tree
from fudge.refs import read_ref, write_ref
from fudge.utils import FudgeException


Commit = namedtuple('Commit', ['id', 'tree', 'parents', 'author', 'committer', 'message'])


class Author(object):
    def __init__(self, name, email, timestamp, offset):
        self.name = name
        self.email = email
        self.timestamp = timestamp
        self.offset = offset

    @property
    def datetime(self):
        timestamp = float(self.timestamp)

        hours, minutes = int(self.offset[0:3]), int(self.offset[3:5])
        timedelta = datetime.timedelta(hours=hours, minutes=minutes)
        timezone = datetime.timezone(timedelta)

        dt = datetime.datetime.fromtimestamp(timestamp, timezone)
        return '{} {}'.format(dt.strftime('%c'), self.offset)


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
    tree_id = write_tree()
    parent = read_ref('HEAD')

    commit = build_commit(tree_id, [parent], message)
    store_object(commit)

    write_ref('HEAD', commit.id)

    return commit.id


def parse_user_and_datetime(parts, expected_keyword):
    if len(parts) < 5:
        raise FudgeException('invalid commit')

    keyword, name, email, timestamp, offset = (
        parts[0], ' '.join(parts[1:-3]), parts[-3], parts[-2], parts[-1])

    if keyword != expected_keyword:
        raise FudgeException('invalid commit')

    email = email.lstrip('<').rstrip('>')
    return Author(name, email, timestamp, offset)


def parse_author(parts):
    return parse_user_and_datetime(parts, 'author')


def parse_committer(parts):
    return parse_user_and_datetime(parts, 'committer')


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

    author = parse_author(line)
    committer = parse_committer(next(lines).split())

    return Commit(obj.id, tree_id, parents, author, committer, message)


def read_commit(object_id):
    obj = load_object(object_id)
    return parse_commit(obj)


def iter_commits():
    object_id = read_ref('HEAD')

    while True:
        commit = read_commit(object_id)

        yield commit

        if not commit.parents:
            break

        object_id = commit.parents[0]
