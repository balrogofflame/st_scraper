DEFAULT_USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/124.0.0.0 Safari/537.36'
)


def build_headers(accept_language=None, extra_headers=None):
    headers = {
        'User-Agent': DEFAULT_USER_AGENT
    }

    if accept_language:
        headers['Accept-Language'] = accept_language

    if extra_headers:
        headers.update(extra_headers)

    return headers
