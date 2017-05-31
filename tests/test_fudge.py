from fudge.commands import cat_file, hash_object, ls_files


def test_init(repo):
    assert repo.join('.fudge').join('objects').check(dir=True)


def test_hash_object_from_file(capsys, repo):
    test = repo.join('test.txt')
    test.write('test content\n')

    hash_object(str(test))

    out, err = capsys.readouterr()
    assert out.rstrip() == 'd670460b4b4aece5915caf5c68d12f560a9fe3e4'


def test_cat_file(capsys, repo):
    test = repo.join('test.txt')
    test.write('test content\n')

    hash_object(str(test), write=True)

    out, err = capsys.readouterr()
    digest = out.rstrip('\n')
    cat_file(digest, show_contents=True)

    out, err = capsys.readouterr()
    assert out == 'test content\n'


def test_ls_files(capsys, repo):
    with open('tests/index', 'rb') as f:
        data = f.read()
    index = repo.join('.fudge').join('index')
    index.write(data, mode='wb')

    ls_files(stage=True)

    expected = [
        '100644 83c831f0b085c70509b1fbb0a0131a9a32e691ac README.md',
        '100644 09907203e86ff6490c525b989c65bdef64aa706a hello.py'
    ]

    out, err = capsys.readouterr()
    assert out.rstrip('\n').split('\n') == expected
