# fudge

Fudge is an implementation of Git's basics in Python.

My end goal with this project is to learn about Git internals, not to develop a
fully-fledged implementation of Git. Here are the planned features:
- Store and load objects to and from the object store (`.fudge/objects/`).
- Read and write blob, tree and commit objects.
- Read and write version 2 Git index files, with no extensions.
- Read and write refs and symbolic refs.
- Read and write undeltified version 2 pack files.
- Talk to Git servers via HTTP(S) using the "smart" protocol.

Support for branches, merge operations, revisions (commit-ish, tree-ish), tags…
is not currently planned.

In short fudge could be used to create and visualize a simple history, push it
to a remote Git server, and clone repositories.

Fudge does not delete or overwrite any file or directory (e.g. the `rm` command
only deletes files from the index).

## Requirements

- Python (>= 3.4)
- pip
- virtualenv

## Usage

Set up a development environment:
```
$ virtualenv venv
$ source venv/bin/activate
$ make install
```

Run tests:
```
$ make test
```

Show help messages:
```
$ fudge --help
$ fudge <command> --help
```

Create a commit using only plumbing commands:
```
$ fudge init
Initialized empty Git repository in…
$ echo 'test content' | fudge hash-object -w --stdin
d670460b4b4aece5915caf5c68d12f560a9fe3e4
$ fudge cat-file -p d67046
test content
$ fudge update-index --add --cacheinfo \
    100644,d670460b4b4aece5915caf5c68d12f560a9fe3e4,test.txt
$ fudge ls-files --stage
100644 d670460b4b4aece5915caf5c68d12f560a9fe3e4 test.txt
$ fudge write-tree
80865964295ae2f11d27383e5f9c0b58a8ef21da
$ fudge commit-tree -m 'Initial commit' 808659
<commit id>
$ fudge update-ref HEAD <commit id>
```

## Implemented commands
### Plumbing

- `cat-file`
- `checkout-index`
- `commit-tree`
- `hash-object`
- `ls-files`
- `ls-tree`
- `read-tree`
- `symbolic-ref` (only supports the `HEAD` symbolic ref)
- `update-index`
- `update-ref`
- `write-tree`

### Porcelain

- `add`
- `clone`
- `commit`
- `init`
- `log`
- `rm`

## References

- [Pro Git's "Git Internals" chapter](https://git-scm.com/book/en/v2/Git-Internals-Plumbing-and-Porcelain)
- [Git's technical documentation](https://github.com/git/git/tree/master/Documentation/technical)
- [Git Files Data Formats](http://git.rsbx.net/Documents/Git_Data_Formats.txt)

## License

This project is licensed under the terms of the MIT license.
