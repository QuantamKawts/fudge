import os

from fudge.utils import makedirs, write_file


def get_repository_path():
    basedir = os.environ.get('FUDGE_DIR')
    if basedir:
        basedir = os.path.abspath(basedir)
    else:
        basedir = os.getcwd()
    return os.path.join(basedir, '.fudge')


def create_repository():
    basedir = get_repository_path()
    subdirs = ['objects', 'refs/heads']

    for subdir in subdirs:
        path = os.path.join(basedir, subdir)
        makedirs(path)

    path = os.path.join(basedir, 'HEAD')
    if not os.path.exists(path):
        write_file(path, 'ref: refs/heads/master\n', mode='w')
