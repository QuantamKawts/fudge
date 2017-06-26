import binascii
import struct


class Builder(object):
    def __init__(self, padding=True):
        """Initialize a Builder."""
        self.padding = padding

        self.buffer = bytearray([0] * 16)
        self.offset = 0

    @property
    def data(self):
        return self.buffer[:self.offset]

    def set(self, value):
        length = len(value)
        if self.offset + length >= len(self.buffer):
            self.buffer.extend([0] * len(self.buffer))
        self.buffer[self.offset:self.offset+length] = value
        self.offset += length

    def set_string(self, value, encoding):
        value = bytes(value, encoding)
        value += b'\0'
        self.set(value)

        if self.padding:
            self.offset = self.pad(self.offset, 8)

    def pack(self, fmt, *args):
        value = struct.pack(fmt, *args)
        self.set(value)

    def pad(self, value, to):
        reminder = value % to
        if reminder > 0:
            value += to - reminder
        return value

    def set_s1(self, value):
        """Write a 1-byte signed integer."""
        self.pack('!b', value)

    def set_u1(self, value):
        """Write a 1-byte unsigned integer."""
        self.pack('!B', value)

    def set_s2(self, value):
        """Write a 2-byte signed integer."""
        self.pack('!h', value)

    def set_u2(self, value):
        """Write a 2-byte unsigned integer."""
        self.pack('!H', value)

    def set_s4(self, value):
        """Write a 4-byte signed integer."""
        self.pack('!i', value)

    def set_u4(self, value):
        """Write a 4-byte unsigned integer."""
        self.pack('!I', value)

    def set_s8(self, value):
        """Write an 8-byte signed integer."""
        self.pack('!q', value)

    def set_u8(self, value):
        """Write an 8-byte unsigned integer."""
        self.pack('!Q', value)

    def set_f4(self, value):
        """Write a 4-byte float."""
        self.pack('!f', value)

    def set_sha1(self, value):
        """Write a SHA-1 checksum."""
        checksum = binascii.unhexlify(value)
        self.set(checksum)

    def set_utf8(self, value):
        """Write a UTF-8 encoded string."""
        self.set_string(value, 'utf-8')
