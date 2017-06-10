import zlib

from fudge.object import Object, ObjectType
from fudge.parsing.parser import Parser
from fudge.utils import FudgeException


def parse_pack(data):
    parser = Parser(data)
    objects = {}

    if parser.get(4) != b'PACK':
        raise FudgeException('invalid pack file')

    version = parser.get_u4()
    if version != 2:
        raise FudgeException('unsupported pack file version: {}'.format(version))

    num_objects = parser.get_u4()
    for _ in range(num_objects):
        obj, base_object_id = parse_packed_object(parser)
        if ObjectType.from_name(obj.type) == ObjectType.DELTA_BASE:
            base_object = objects[base_object_id]
            obj = parse_delta_hunks(obj.contents, base_object)

        objects[obj.id] = obj

    # TODO: verify checksum
    digest = parser.get_sha1()

    return objects.values()


def parse_packed_object(parser):
    byte = parser.get_u1()
    extended = (byte >> 7) & 1

    object_type = (byte >> 4) & 0x7
    if not ObjectType.exists(object_type):
        raise FudgeException('invalid packed object type: {}'.format(object_type))
    elif object_type == ObjectType.DELTA_OFFSET:
        raise FudgeException('unsupported packed object type: {}'.format(object_type))

    size = byte & 0xf

    shift = 4
    while extended:
        byte = parser.get_u1()
        extended = (byte >> 7) & 1
        size |= (byte & 0x7f) << shift
        shift += 7

    base_object_id = None
    if object_type == ObjectType.DELTA_BASE:
        base_object_id = parser.get_sha1()

    decompress = zlib.decompressobj()
    contents = decompress.decompress(parser.data[parser.offset:])
    if len(contents) != size:
        raise FudgeException('invalid object length')

    # The pack file format does not contain the length of the compressed data,
    # and Python's zlib does not give us a way to directly access the number
    # of bytes read during decompression.
    # To work around that, we pass the whole buffer to Python's zlib and use
    # the length of the remaining data to update the parser's offset.
    parser.offset = len(parser.data) - len(decompress.unused_data)

    name = ObjectType.to_name(object_type)

    return Object(name, size, contents), base_object_id


def parse_delta_hunks(data, base_object):
    parser = Parser(data)
    base_object_length = parser.get_leb128()
    result_object_length = parser.get_leb128()

    if base_object.size != base_object_length:
        raise FudgeException('invalid base object length')

    source = base_object.contents
    dest = bytearray()

    while not parser.eof:
        opcode = parser.get_u1()

        copy_hunk = (opcode >> 7) & 1
        if copy_hunk:
            copy_offset = 0
            copy_length = 0

            for i in range(4):
                if opcode & 1:
                    copy_offset |= parser.get_u1() << (i * 8)
                opcode >>= 1

            for i in range(2):
                if opcode & 1:
                    copy_length |= parser.get_u1() << (i * 8)
                opcode >>= 1

            if not copy_length:
                copy_length = 1 << 16

            copy_from_dest = opcode & 1
            if copy_from_dest:
                dest += dest[copy_offset:copy_offset+copy_length]
            else:
                dest += source[copy_offset:copy_offset+copy_length]
        else:
            length = opcode & 0x7f
            insert_data = parser.get(length)
            dest += insert_data

    if len(dest) != result_object_length:
        raise FudgeException('invalid result object length')

    return Object(base_object.type, result_object_length, dest)


if __name__ == '__main__':
    from fudge.utils import read_file
    data = read_file('pack')
    parse_pack(data)
