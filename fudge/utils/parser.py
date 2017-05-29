import binascii
import struct


class Parser(object):
    def __init__(self, data):
        """Initialize a Parser."""
        self.data = data

        self.offset = 0

    def get(self, n):
        """Read a fixed number of bytes."""
        value = self.data[self.offset:self.offset+n]
        self.offset += n
        return value

    def get_string(self, encoding):
        string = b''

        char = self.get(1)
        while char != b'\0':
            string += char
            char = self.get(1)

        self.offset = self.pad(self.offset, 8)
        return str(string, encoding)

    def unpack(self, fmt, size):
        value = self.get(size)
        unpacked = struct.unpack(fmt, value)[0]
        return unpacked

    def pad(self, value, to):
        reminder = value % to
        if reminder > 0:
            value += to - reminder
        return value

    def get_s1(self):
        """Read a 1-byte signed integer."""
        return self.unpack('!b', 1)

    def get_u1(self):
        """Read a 1-byte unsigned integer."""
        return self.unpack('!B', 1)

    def get_s2(self):
        """Read a 2-byte signed integer."""
        return self.unpack('!h', 2)

    def get_u2(self):
        """Read a 2-byte unsigned integer."""
        return self.unpack('!H', 2)

    def get_s4(self):
        """Read a 4-byte signed integer."""
        return self.unpack('!i', 4)

    def get_u4(self):
        """Read a 4-byte unsigned integer."""
        return self.unpack('!I', 4)

    def get_s8(self):
        """Read an 8-byte signed integer."""
        return self.unpack('!q', 8)

    def get_u8(self):
        """Read an 8-byte unsigned integer."""
        return self.unpack('!Q', 8)

    def get_f4(self):
        """Read a 4-byte float."""
        return self.unpack('!f', 4)

    def get_sha1(self):
        """Read a SHA-1 checksum."""
        checksum = binascii.hexlify(self.get(20))
        return str(checksum, 'utf-8')

    def get_utf8(self):
        """Read a UTF-8 encoded string."""
        return self.get_string('utf-8')
