import requests

from fudge import __version__


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
        raise Exception('fudge: repository {} does not exist'.format(repo_url))

    content_type = response.headers.get('Content-Type')
    if content_type != 'application/x-{}-advertisement'.format(service):
        raise Exception('fudge: invalid response Content-Type: {}'.format(content_type))

    lines = iter(response.text.split('\n'))

    service_line = parse_pkt_line(next(lines))
    if service_line != '# service={}'.format(service):
        raise Exception('fudge: invalid service line')

    info = parse_pkt_line(next(lines))
    head, capabilities = info.split('\0')
    head_digest = head.split()[0]
    capabilities = capabilities.split()

    refs = {}
    while True:
        ref_line = parse_pkt_line(next(lines))
        if len(ref_line) == 0:
            break

        digest, ref = ref_line.split()
        refs[ref] = digest

    return head_digest, refs


def upload_pack(repo_url):
    repo_url = repo_url.rstrip('/')
    service = 'git-upload-pack'

    head_digest, refs = discover_refs(repo_url, service)

    command = 'want {}'.format(head_digest)
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
        raise Exception('fudge: repository {} does not exist'.format(repo_url))

    content_type = response.headers.get('Content-Type')
    if content_type != 'application/x-{}-result'.format(service):
        raise Exception('fudge: invalid response Content-Type: {}'.format(content_type))

    lines = iter(response.content.split(b'\n', 1))
    status = parse_pkt_line(next(lines))
    if status != b'NAK':
        raise Exception('fudge: requested pack file not found')

    return next(lines)


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
