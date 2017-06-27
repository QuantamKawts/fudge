import pytest

from fudge.index import read_index, write_index
from fudge.utils import FudgeException, read_file

from conftest import get_destination_path


@pytest.mark.fudgefiles(['index_invalid_checksum', 'index'])
def test_read_index_with_an_invalid_checksum(repo):
    with pytest.raises(FudgeException) as exception:
        read_index()
    assert 'bad index file checksum' in str(exception.value)


@pytest.mark.fudgefiles(['index_invalid_magic', 'index'])
def test_read_index_with_an_invalid_magic(repo):
    with pytest.raises(FudgeException) as exception:
        read_index()
    assert 'invalid index file magic' in str(exception.value)


@pytest.mark.fudgefiles(['index_invalid_version', 'index'])
def test_read_index_with_an_invalid_version(repo):
    with pytest.raises(FudgeException) as exception:
        read_index()
    assert 'unsupported index file version' in str(exception.value)


@pytest.mark.fudgefiles(['index_valid', 'index'])
def test_read_index_successfully(repo):
    expected = [
        '.gitignore',
        'README.md',
        'fudge/__init__.py',
        'tests/data/index',
        'tests/test_fudge.py',
    ]
    index = read_index()
    assert [entry.path for entry in index] == expected


@pytest.mark.fudgefiles(['index_valid', 'index'])
def test_read_and_write_index_successfully(repo):
    path = get_destination_path('index')
    before = read_file(path)

    index = read_index()
    write_index(index)

    after = read_file(path)
    assert before == after
