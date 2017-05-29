from fudge.commands import cat_file, hash_object


def test_init(repo):
    assert repo.join('.fudge').join('objects').check(dir=True)


def test_hash_object_from_file(capsys, repo):
    test = repo.join('test.txt')
    test.write('test content\n')

    hash_object(path=test.strpath, stdin=False, write=False)

    out, err = capsys.readouterr()
    assert out == 'd670460b4b4aece5915caf5c68d12f560a9fe3e4\n'


def test_cat_file(capsys, repo):
    test = repo.join('test.txt')
    test.write('test content\n')

    hash_object(path=test.strpath, stdin=False, write=True)

    out, err = capsys.readouterr()
    digest = out.rstrip('\n')
    cat_file(digest, show_type=False, show_size=False, show_contents=True)

    out, err = capsys.readouterr()
    assert out == 'test content\n'
