import pytest

from fudge.commands import cmd_cat_file, cmd_hash_object, cmd_ls_files, cmd_symbolic_ref


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


def test_ls_files(capsys, repo):
    with open('tests/index', 'rb') as f:
        data = f.read()
    index = repo.join('.fudge').join('index')
    index.write(data, mode='wb')

    cmd_ls_files(stage=True)

    expected = [
        '100644 83c831f0b085c70509b1fbb0a0131a9a32e691ac README.md',
        '100644 09907203e86ff6490c525b989c65bdef64aa706a hello.py'
    ]

    out, err = capsys.readouterr()
    assert out.rstrip('\n').split('\n') == expected


def test_symbolic_ref(capsys, repo):
    cmd_symbolic_ref('HEAD')
    out, _ = capsys.readouterr()
    assert out == 'refs/heads/master\n'

    cmd_symbolic_ref('HEAD', short=True)
    out, _ = capsys.readouterr()
    assert out == 'master\n'

    with pytest.raises(SystemExit):
        cmd_symbolic_ref('../../etc/passwd')
    out, _ = capsys.readouterr()
    assert 'invalid name' in out

    with pytest.raises(SystemExit):
        cmd_symbolic_ref('not_an_existing_file')
    out, _ = capsys.readouterr()
    assert 'ref file does not exist' in out

    cmd_symbolic_ref('HEAD', 'refs/heads/test')
    cmd_symbolic_ref('HEAD')
    out, _ = capsys.readouterr()
    assert out == 'refs/heads/test\n'
