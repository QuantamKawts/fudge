import os


def makedirs(path):
    """Create a path."""
    if not os.path.exists(path):
        os.makedirs(path)


def get_repository_path():
    path = os.environ.get('FUDGE_DIR')
    if path:
        path = os.path.abspath(path)
    else:
        path = os.path.join(os.getcwd(), '.fudge')
    return path
