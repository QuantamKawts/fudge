from collections import OrderedDict

from fudge.index import Index, read_index, write_index
from fudge.object import Object, load_object, store_object
from fudge.parsing.builder import Builder
from fudge.parsing.parser import Parser
from fudge.utils import FudgeException


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


def iter_tree(root, recurse):
    for child in root:
        yield child

        if child.is_branch and recurse:
            yield from iter_tree(child, recurse)


def print_tree(root, recurse):
    for node in iter_tree(root, recurse):
        if node.is_branch and recurse:
            continue

        type_ = 'tree' if node.is_branch else 'blob'
        print('{:0>6} {} {} {}'.format(node.mode, type_, node.object_id, node.name))


def build_tree_from_object2(root):
    obj = load_object(root.object_id)
    if obj.type != 'tree':
        raise FudgeException('the specified object is not a tree')

    parser = Parser(obj.contents, padding=False)
    while not parser.eof:
        info = parser.get_utf8()
        mode, name = info.split()
        object_id = parser.get_sha1()

        node = Node(name, mode, object_id)
        root.add(node)

        if mode == '40000':
            build_tree_from_object2(node)

    return root


def build_tree_from_object(object_id):
    root = Node('root', None, object_id)
    return build_tree_from_object2(root)


def read_tree2(index, root, basepath):
    for child in root:
        path = basepath + child.name
        if child.is_branch:
            read_tree2(index, child, path + '/')
        else:
            index.add_object(child.mode, child.object_id, path)


def read_tree(object_id):
    index = Index()
    root = build_tree_from_object(object_id)
    read_tree2(index, root, '')
    write_index(index)


def build_tree_from_index():
    root = Node('root', None, None)

    index = read_index()
    for entry in index:
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
    root = build_tree_from_index()
    return write_tree2(root)
