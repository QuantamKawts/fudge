import pytest

from fudge.object import Object, load_object, store_object
from fudge.utils import FudgeException


def test_object_id_is_valid():
    contents = 'test content\n'
    obj = Object('blob', len(contents), contents)
    assert obj.id == 'd670460b4b4aece5915caf5c68d12f560a9fe3e4'


def test_load_object_unsuccessfully(repo):
    with pytest.raises(FudgeException) as exception:
        load_object('not_a_valid_object_id')
    assert 'invalid object name' in str(exception.value)

    with pytest.raises(FudgeException) as exception:
        load_object('abaddecaf')
    assert 'does not exist' in str(exception.value)


def test_store_and_load_object_successfully(repo):
    contents = 'test content\n'
    obj = Object('blob', len(contents), contents)
    store_object(obj)

    obj2 = load_object(obj.id)

    assert obj.type == obj2.type
    assert obj.size == obj2.size
    assert obj.contents == obj2.contents
