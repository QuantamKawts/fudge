import configparser
import os

from fudge.utils import FudgeException, issafe


def get_config_path():
    """Return the absolute path to the global Git configuration file."""
    basedir = os.path.expanduser('~')
    return os.path.join(basedir, '.gitconfig')


def get_config_value(section, option, *, path=None):
    """Get a value from the global Git configuration file."""
    path = path or get_config_path()
    if not os.path.exists(path):
        raise FudgeException('the Git configuration file {} does not exist'.format(path))

    config = configparser.ConfigParser(strict=False)
    config.read(path)

    value = config.get(section, option, fallback=None)
    if not issafe(value):
        raise FudgeException('invalid value')

    return value
