from collections import OrderedDict, namedtuple

from fudge.index import read_index
from fudge.object import Object, store_object
from fudge.parsing.builder import Builder
from fudge.parsing.parser import Parser
from fudge.utils import FudgeException


class Tree(object):
    def __init__(self):
        self.entries = []

    def add(self, entry):
        self.entries.append(entry)


TreeEntry = namedtuple('TreeEntry', ['mode', 'path', 'object_id'])


def parse_tree(obj):
    if obj.type != 'tree':
        raise FudgeException('the specified object is not a tree')

    tree = Tree()

    parser = Parser(obj.contents, padding=False)
    while not parser.eof:
        info = parser.get_utf8()
        mode, path = info.split()
        object_id = parser.get_sha1()

        entry = TreeEntry(mode, path, object_id)
        tree.add(entry)

    return tree


class Node(object):
    def __init__(self, name, mode, object_id):
        self.name = name
        self.mode = mode
        self.object_id = object_id

        self.children = OrderedDict()

    def __iter__(self):
        for child in self.children.values():
            yield child

    def add(self, child):
        self.children[child.name] = child

    def get(self, name):
        return self.children.get(name)

    @property
    def is_branch(self):
        return len(self.children) > 0

    @property
    def is_leaf(self):
        return len(self.children) == 0


def build_tree():
    root = Node('root', None, None)

    index = read_index()
    for entry in index.entries:
        parts = entry.path.split('/')
        if len(parts) == 1:
            path, filename = [], parts[0]
        else:
            path, filename = parts[:-1], parts[-1]

        current = root
        for dirname in path:
            if not current.get(dirname):
                node = Node(dirname, '40000', None)
                current.add(node)
            current = current.get(dirname)

        node = Node(filename, entry.perms, entry.object_id)
        current.add(node)

    return root


def print_tree(root):
    for child in root:
        print(child.mode, child.object_id, child.name)
        if child.is_branch:
            print_tree(child)


def write_tree2(root):
    builder = Builder(padding=False)
    for child in root:
        if child.is_branch:
            object_id = write_tree2(child)
            child.object_id = object_id

        info = '{} {}'.format(child.mode, child.name)
        builder.set_utf8(info)
        builder.set_sha1(child.object_id)

    data = builder.data
    obj = Object('tree', len(data), data)
    store_object(obj)

    return obj.id


def write_tree():
    root = build_tree()
    return write_tree2(root)
