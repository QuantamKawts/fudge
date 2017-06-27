import pytest

from fudge.commands import cmd_cat_file, cmd_hash_object, cmd_ls_files


def test_init(repo):
    assert repo.join('.fudge').join('objects').check(dir=True)


def test_hash_object_from_file(capsys, repo):
    test = repo.join('test.txt')
    test.write('test content\n')

    cmd_hash_object(str(test))

    out, err = capsys.readouterr()
    assert out.rstrip() == 'd670460b4b4aece5915caf5c68d12f560a9fe3e4'


def test_cat_file(capsys, repo):
    test = repo.join('test.txt')
    test.write('test content\n')

    cmd_hash_object(str(test), write=True)

    out, err = capsys.readouterr()
    digest = out.rstrip('\n')
    cmd_cat_file(digest, show_contents=True)

    out, err = capsys.readouterr()
    assert out == 'test content\n'

    cmd_cat_file(digest[:8], show_contents=True)

    out, err = capsys.readouterr()
    assert out == 'test content\n'


@pytest.mark.fudgefiles(['index_valid', 'index'])
def test_ls_files(capsys, repo):
    expected = [
        '.gitignore',
        'README.md',
        'fudge/__init__.py',
        'tests/data/index',
        'tests/test_fudge.py',
    ]

    cmd_ls_files()

    out, err = capsys.readouterr()
    assert out.rstrip('\n').split('\n') == expected
