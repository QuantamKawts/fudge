import os
import shutil

import pytest

from fudge.repository import create_repository, get_repository_path
from fudge.utils import makedirs


def get_data_path(path):
    basedir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(basedir, 'data', path)


def get_destination_path(path):
    basedir = get_repository_path()
    destpath = os.path.join(basedir, path)

    destdir = os.path.dirname(destpath)
    makedirs(destdir)

    return destpath


@pytest.fixture
def repo(request, tmpdir):
    os.chdir(str(tmpdir))
    create_repository()

    mark = request.keywords.get('fudgefiles')
    if mark:
        for srcpath, destpath in mark.args:
            srcpath = get_data_path(srcpath)
            destpath = get_destination_path(destpath)

            shutil.copy(srcpath, destpath)

    yield tmpdir
