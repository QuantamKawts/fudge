import os

from fudge.utils import makedirs, write_file


def get_working_tree_path():
    env = os.environ.get('FUDGE_DIR')
    if env:
        basedir = os.path.abspath(env)
    else:
        basedir = os.getcwd()
    return basedir


def get_repository_path():
    basedir = get_working_tree_path()
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
