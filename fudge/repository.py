import os

from fudge.utils import FudgeException, makedirs, write_file


def find_repository_path():
    current = os.getcwd()
    while True:
        path = os.path.join(current, '.fudge')
        if os.path.exists(path):
            return path

        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent

    return None


def get_repository_path():
    repo = find_repository_path()

    if not repo:
        raise FudgeException('repository not found')

    return repo


def get_working_tree_path():
    repo = get_repository_path()
    return os.path.dirname(repo)


def create_repository(basedir=None):
    if basedir:
        basedir = os.path.abspath(basedir)
    else:
        basedir = os.getcwd()

    basedir = os.path.join(basedir, '.fudge')
    reinit = os.path.exists(basedir)

    subdirs = ['objects', 'refs/heads']

    for subdir in subdirs:
        path = os.path.join(basedir, subdir)
        makedirs(path)

    path = os.path.join(basedir, 'HEAD')
    if not os.path.exists(path):
        write_file(path, 'ref: refs/heads/master\n', mode='w')

    return basedir, reinit
