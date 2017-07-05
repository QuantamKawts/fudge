import os
import pytest
import shutil

from fudge.config import get_config_path, get_config_value
from fudge.utils import FudgeException

from tests.conftest import get_data_path


def test_path():
    assert get_config_path().endswith('/.gitconfig')


def test_value():
    path = get_data_path('config/simple')
    assert get_config_value('user', 'name', path=path) == "Hatsune Miku"
    assert get_config_value('user', 'email', path=path) == "vocaloid@crypton.co.jp"


def test_repeated_values(tmpdir):
    path = os.path.join(str(tmpdir), '.gitconfig')
    shutil.copy(get_data_path('config/repeated'), path)

    # Repeated key "name" -- we expect to see the last value.
    assert get_config_value('user', 'name', path=path) == "Kagamine Rin"

    # The section name [user] is repeated; we should still see non-overridden values.
    assert get_config_value('user', 'email', path=path) == "vocaloid@crypton.co.jp"


def test_unsafe_value():
    path = get_data_path('config/unsafe')

    with pytest.raises(FudgeException) as exception:
        get_config_value('user', 'name', path=path)
    assert 'invalid value' in str(exception.value)
