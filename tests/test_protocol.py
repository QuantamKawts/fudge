import pytest
import responses

from fudge.protocol import discover_refs
from fudge.utils import FudgeException, read_file

from tests.conftest import get_data_path


@responses.activate
def test_discover_refs():
    repo_url = 'https://github.com/bovarysme/fudge.git'
    service = 'git-upload-pack'

    url = '{}/info/refs?service={}'.format(repo_url, service)
    content_type = 'application/x-{}-advertisement'.format(service)

    path = get_data_path('protocol/advertisement')
    body = read_file(path)

    with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
        # Send a response with an invalid status.
        rsps.add(responses.GET, url, match_querystring=True, status=401)

        # Send a response with an invalid Content-Type.
        rsps.add(responses.GET, url, match_querystring=True, status=200, content_type='text/plain')

        # Send a valid response.
        rsps.add(
            responses.GET, url, match_querystring=True,
            status=200, content_type=content_type, body=body
        )

        with pytest.raises(FudgeException) as exception:
            discover_refs(repo_url, 'git-upload-pack')
        assert 'repository {} does not exist'.format(repo_url) in str(exception.value)

        with pytest.raises(FudgeException) as exception:
            discover_refs(repo_url, 'git-upload-pack')
        assert 'invalid Content-Type' in str(exception.value)

        head_commit_id = discover_refs(repo_url, 'git-upload-pack')
        assert head_commit_id == '5adb9f329fe0bc8a882e886923f6bffcb77c986e'
