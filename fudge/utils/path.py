import os


def makedirs(path):
    """Create a path."""
    if not os.path.exists(path):
        os.makedirs(path)


def get_repository_path():
    basedir = os.environ.get('FUDGE_DIR')
    if basedir:
        basedir = os.path.abspath(basedir)
    else:
        basedir = os.getcwd()
    return os.path.join(basedir, '.fudge')
