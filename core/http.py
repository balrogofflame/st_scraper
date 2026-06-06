from core.settings import app_config


def build_headers(accept_language=None, extra_headers=None, user_agent=None):
    headers = {
        'User-Agent': user_agent or app_config.scraper_user_agent
    }

    if accept_language:
        headers['Accept-Language'] = accept_language

    if extra_headers:
        headers.update(extra_headers)

    return headers
