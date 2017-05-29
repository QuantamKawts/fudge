import os

import pytest

from fudge.commands import init


@pytest.fixture
def repo(tmpdir):
    repo = tmpdir.mkdir('.fudge')
    os.environ['FUDGE_DIR'] = repo.strpath
    init()

    yield tmpdir
