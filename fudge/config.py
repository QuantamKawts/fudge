import configparser
import os

from fudge.utils import FudgeException, issafe


def get_config_path():
    """Return the absolute path to the global Git configuration file."""
    basedir = os.path.expanduser('~')
    return os.path.join(basedir, '.gitconfig')


def get_config_value(section, option):
    """Get a value from the global Git configuration file.

    Examples:
        >>> get_config_value('user', 'name')
        'alice'

        >>> get_config_value('user', 'nonexistent_option')
        None
    """
    path = get_config_path()
    if not os.path.exists(path):
        raise FudgeException('the global Git configuration file {} does not exist'.format(path))

    config = configparser.ConfigParser()
    config.read(path)

    value = config.get(section, option, fallback=None)
    if not issafe(value):
        raise FudgeException('invalid value')

    return value