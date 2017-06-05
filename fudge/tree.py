from collections import namedtuple

from fudge.index import read_index
from fudge.parsing.builder import Builder
from fudge.parsing.parser import Parser


class Tree(object):
    def __init__(self):
        self.entries = []

    def add(self, entry):
        self.entries.append(entry)


TreeEntry = namedtuple('TreeEntry', ['mode', 'path', 'checksum'])


def parse_tree(tree):
    parser = Parser(tree, padding=False)

    tree = Tree()

    while not parser.eof:
        info = parser.get_utf8()
        mode, path = info.split()
        checksum = parser.get_sha1()

        entry = TreeEntry(mode, path, checksum)
        tree.add(entry)

    return tree


def build_tree():
    builder = Builder(padding=False)

    index = read_index()
    for entry in index.entries:
        info = '{} {}'.format(entry.perms, entry.path)
        builder.set_utf8(info)
        builder.set_sha1(entry.checksum)

    header = 'tree {}'.format(len(builder.data))
    header_builder = Builder(padding=False)
    header_builder.set_utf8(header)

    return header_builder.data + builder.data
