import os

from fudge.repository import get_repository_path
from fudge.utils import FudgeException, read_file, write_file


def get_symbolic_ref_path():
    basedir = get_repository_path()
    return os.path.join(basedir, 'HEAD')


def valid_ref(ref):
    blacklist = [chr(value) for value in range(20)]
    blacklist.extend([' ', '*', ':', '?', '[', '^', '~', '/.', '..'])
    return ref.startswith('refs/') and not ref.endswith('/') \
        and not any(char in ref for char in blacklist)


def read_symbolic_ref():
    path = get_symbolic_ref_path()
    if not os.path.exists(path):
        raise FudgeException('the symbolic ref file does not exist')

    data = read_file(path, mode='r').rstrip('\n')

    lines = data.split('\n')
    if len(lines) > 1:
        raise FudgeException('invalid symbolic ref file')

    parts = data.split(' ')
    if len(parts) != 2 and parts[0] != 'ref:':
        raise FudgeException('invalid symbolic ref file')

    ref = parts[1]
    if not valid_ref(ref):
        raise FudgeException('invalid ref')

    return ref


def write_symbolic_ref(ref):
    if not valid_ref(ref):
        raise FudgeException('invalid ref')

    path = get_symbolic_ref_path()
    write_file(path, 'ref: {}\n'.format(ref), mode='w')
