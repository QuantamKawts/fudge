# fudge

Fudge is an implementation of Git in Python, written for learning purposes.

## Requirements

- Python (>= 3.3)
- pip
- virtualenv

## Usage

```
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r test-requirements.txt
$ pip install -e .
$ fudge init
Initialized empty Git repository in…
$ echo 'test content' | fudge hash-object -w --stdin
d670460b4b4aece5915caf5c68d12f560a9fe3e4
$ fudge cat-file -p d670460b4b4aece5915caf5c68d12f560a9fe3e4
test content
$ fudge update-index --add --cacheinfo \
    100644,d670460b4b4aece5915caf5c68d12f560a9fe3e4,test.txt
$ fudge ls-files --stage
100644 d670460b4b4aece5915caf5c68d12f560a9fe3e4 test.txt
```

Show help messages:
```
$ fudge --help
$ fudge <command> --help
```

Run tests:
```
$ pytest
```

## Implemented commands
### Plumbing

- `hash-object`
- `cat-file`
- `update-index`
- `ls-files`

### Porcelain

- `init`

## References

- [Pro Git's "Git Internals" chapter](https://git-scm.com/book/en/v2/Git-Internals-Plumbing-and-Porcelain)
- [Git's technical documentation](https://github.com/git/git/tree/master/Documentation/technical)

## License

This project is licensed under the terms of the MIT license.
