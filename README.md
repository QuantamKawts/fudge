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
$ pip install -e .
$ fudge init
Initialized empty Git repository in…
$ echo 'test content' | fudge hash-object -w --stdin
d670460b4b4aece5915caf5c68d12f560a9fe3e4
$ fudge cat-file -p d670460b4b4aece5915caf5c68d12f560a9fe3e4
test content
```

Show help messages:
```
$ fudge --help
$ fudge <command> --help
```

## Implemented commands
### Plumbing

- `hash-object`
- `cat-file`

### Porcelain

- `init`

## References

- [Pro Git's "Git Internals" chapter](https://git-scm.com/book/en/v2/Git-Internals-Plumbing-and-Porcelain)

## License

This project is licensed under the terms of the MIT license.
