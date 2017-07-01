import string

import requests

from fudge import __version__
from fudge.utils import FudgeException


def get_repository_name(repo_url):
    repo_url = repo_url.rstrip('/')
    repo_name = repo_url.split('/')[-1].rstrip('.git')

    whitelist = set([char for char in string.ascii_letters + string.digits + '-_'])
    if not all(char in whitelist for char in repo_name):
        raise FudgeException('invalid repository name')

    return repo_name


def discover_refs(repo_url, service):
    url = '{}/info/refs'.format(repo_url)
    headers = {
        'User-Agent': 'fudge/{}'.format(__version__),
    }
    params = {
        'service': service,
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code not in (200, 304):
        raise FudgeException('repository {} does not exist'.format(repo_url))

    content_type = response.headers.get('Content-Type')
    if content_type != 'application/x-{}-advertisement'.format(service):
        raise FudgeException('invalid response Content-Type: {}'.format(content_type))

    lines = iter(response.text.split('\n'))

    service_line = parse_pkt_line(next(lines))
    if service_line != '# service={}'.format(service):
        raise FudgeException('invalid service line')

    info = parse_pkt_line(next(lines))
    head, capabilities = info.split('\0')
    head_object_id = head.split()[0]
    capabilities = capabilities.split()

    refs = {}
    while True:
        ref_line = parse_pkt_line(next(lines))
        if len(ref_line) == 0:
            break

        object_id, ref = ref_line.split()
        refs[ref] = object_id

    return head_object_id


def upload_pack(repo_url):
    repo_url = repo_url.rstrip('/')
    service = 'git-upload-pack'

    head_object_id = discover_refs(repo_url, service)

    command = 'want {}'.format(head_object_id)
    request = pkt_line(command)
    request += pkt_line()
    request += pkt_line('done')

    url = '{}/{}'.format(repo_url, service)
    headers = {
        'Content-Type': 'application/x-{}-request'.format(service),
        'User-Agent': 'fudge/{}'.format(__version__)
    }
    response = requests.post(url, headers=headers, data=request)
    if response.status_code not in (200, 304):
        raise FudgeException('repository {} does not exist'.format(repo_url))

    content_type = response.headers.get('Content-Type')
    if content_type != 'application/x-{}-result'.format(service):
        raise FudgeException('invalid response Content-Type: {}'.format(content_type))

    lines = iter(response.content.split(b'\n', 1))
    status = parse_pkt_line(next(lines))
    if status != b'NAK':
        raise FudgeException('could not retrieve the requested pack file')

    pack = next(lines)

    return pack, head_object_id


def pkt_line(command=None):
    if not command:
        return '0000'

    length = '{:04x}'.format(len(command) + 5)
    return '{}{}\n'.format(length, command)


def parse_pkt_line(line):
    """Parse a pkt-line."""
    length, data = line[:4], line[4:]
    length = int(length, 16)

    # Skip flush-pkts
    if length == 0 and len(data) > 0:
        length, data = data[:4], data[4:]
        length = int(length, 16)

    return data
