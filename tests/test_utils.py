import os
from fudge.utils import stat
from tests.conftest import get_data_path


def test_stat_bounds(monkeypatch):
    def mockstat(path):
        monkeypatch.undo()
        result = os.stat(path)
        return os.stat_result((
            result.st_mode,
            2 ** 32 + result.st_ino + 1,  # Ensure st_ino > 2 ** 32
            result.st_dev,
            result.st_nlink,
            result.st_uid,
            result.st_gid,
            result.st_size,
            result.st_atime,
            result.st_mtime,
            result.st_ctime,
        ))
    monkeypatch.setattr(os, 'stat', mockstat)

    path = get_data_path('stat')
    result = stat(path)

    for key, value in result.items():
        assert value < 2 ** 32, 'expected {} to have value less than 2 ** 32'.format(key)
