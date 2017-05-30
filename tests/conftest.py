import os

import pytest

from fudge.commands import init


@pytest.fixture
def repo(tmpdir):
    os.environ['FUDGE_DIR'] = tmpdir.strpath
    init()

    yield tmpdir
