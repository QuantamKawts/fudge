from fudge.index import read_index
from fudge.parsing.builder import Builder


def build_tree():
    builder = Builder()

    index = read_index()
    for entry in index.entries:
        info = '{} {}'.format(entry.perms, entry.path)
        builder.set_utf8(info)
        builder.set_sha1(entry.checksum)

    header = 'tree {}'.format(len(builder.data))
    header_builder = Builder()
    header_builder.set_utf8(header)

    return header_builder.data + builder.data
