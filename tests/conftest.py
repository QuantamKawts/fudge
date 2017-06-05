import os

import pytest

from fudge.commands import cmd_init


@pytest.fixture
def repo(tmpdir):
    os.environ['FUDGE_DIR'] = str(tmpdir)
    cmd_init()

    yield tmpdir
