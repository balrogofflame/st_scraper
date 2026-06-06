import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT_DIR / '.env'

DEFAULT_SCRAPER_USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/124.0.0.0 Safari/537.36'
)

DEFAULT_ACCEPT_LANGUAGE_BY_STORE = {
    'ayce': 'zh-TW,zh-Hant;q=0.9,en-US;q=0.8,en;q=0.7',
    'drqq': 'zh-TW,zh-Hant;q=0.9,en-US;q=0.8,en;q=0.7',
    'harryboy': 'zh-TW,zh-Hant;q=0.9,en-US;q=0.8,en;q=0.7',
    'iroha': 'zh-TW,zh-Hant;q=0.9,en-US;q=0.8,en;q=0.7',
    'lelo': 'zh-CN,zh-Hans;q=0.9,zh-TW;q=0.8,en-US;q=0.7,en;q=0.6',
    'playjoy': 'zh-TW,zh-Hant;q=0.9,en-US;q=0.8,en;q=0.7',
    'puresexy': 'zh-TW,zh-Hant;q=0.9,en-US;q=0.8,en;q=0.7',
    'redino': 'zh-TW,zh-Hant;q=0.9,en-US;q=0.8,en;q=0.7',
    'rxing': 'zh-TW,zh-Hant;q=0.9,en-US;q=0.8,en;q=0.7',
    'tenga': 'zh-TW,zh-Hant;q=0.9,en-US;q=0.8,en;q=0.7',
    'womanizer': 'en-US,en;q=0.9',
}

DEFAULT_DELAY_BY_STORE = {
    'harryboy': 0.2,
}

DEFAULT_MAX_CATEGORIES_BY_STORE = {
    'drqq': 300,
    'sallyq': 50,
    'tenga': 300,
}


def _normalize_store_name(store_name):
    return ''.join(
        character if character.isalnum() else '_'
        for character in (store_name or '').upper()
    )


def _read_str(environ, key, default):
    value = environ.get(key)

    if value is None:
        return default

    value = value.strip()
    return value or default


def _read_optional_str(environ, key, default=None):
    value = environ.get(key)

    if value is None:
        return default

    value = value.strip()
    return value or None


def _read_int(environ, key, default):
    value = environ.get(key)

    if value is None or not value.strip():
        return default

    return int(value)


def _read_float(environ, key, default):
    value = environ.get(key)

    if value is None or not value.strip():
        return default

    return float(value)


def _read_optional_int(environ, key, default=None):
    value = environ.get(key)

    if value is None:
        return default

    value = value.strip()

    if not value:
        return None

    return int(value)


@dataclass(frozen=True)
class AppConfig:
    scraper_user_agent: str
    scraper_timeout: int
    scraper_delay: float
    scraper_max_pages: int
    scraper_max_categories: int | None
    exchange_rate_timeout: int

    @classmethod
    def from_env(cls, environ=None):
        env = os.environ if environ is None else environ
        return cls(
            scraper_user_agent=_read_str(env, 'SCRAPER_USER_AGENT', DEFAULT_SCRAPER_USER_AGENT),
            scraper_timeout=_read_int(env, 'SCRAPER_TIMEOUT', 10),
            scraper_delay=_read_float(env, 'SCRAPER_DELAY', 1.0),
            scraper_max_pages=_read_int(env, 'SCRAPER_MAX_PAGES', 100),
            scraper_max_categories=_read_optional_int(env, 'SCRAPER_MAX_CATEGORIES', None),
            exchange_rate_timeout=_read_int(env, 'EXCHANGE_RATE_TIMEOUT', 10),
        )

    def get_scraper_timeout(self, store_name, fallback=None, environ=None):
        env = os.environ if environ is None else environ
        key = f'SCRAPER_{_normalize_store_name(store_name)}_TIMEOUT'
        default = self.scraper_timeout if fallback is None else fallback
        return _read_int(env, key, default)

    def get_scraper_delay(self, store_name, fallback=None, environ=None):
        env = os.environ if environ is None else environ
        key = f'SCRAPER_{_normalize_store_name(store_name)}_DELAY'
        store_default = DEFAULT_DELAY_BY_STORE.get(store_name, self.scraper_delay)
        default = store_default if fallback is None else fallback
        return _read_float(env, key, default)

    def get_scraper_max_pages(self, store_name, fallback=None, environ=None):
        env = os.environ if environ is None else environ
        key = f'SCRAPER_{_normalize_store_name(store_name)}_MAX_PAGES'
        default = self.scraper_max_pages if fallback is None else fallback
        return _read_int(env, key, default)

    def get_scraper_max_categories(self, store_name, fallback=None, environ=None):
        env = os.environ if environ is None else environ
        key = f'SCRAPER_{_normalize_store_name(store_name)}_MAX_CATEGORIES'
        store_default = DEFAULT_MAX_CATEGORIES_BY_STORE.get(store_name, self.scraper_max_categories)
        default = store_default if fallback is None else fallback
        return _read_optional_int(env, key, default)

    def get_scraper_accept_language(self, store_name, fallback=None, environ=None):
        env = os.environ if environ is None else environ
        key = f'SCRAPER_{_normalize_store_name(store_name)}_ACCEPT_LANGUAGE'
        store_default = DEFAULT_ACCEPT_LANGUAGE_BY_STORE.get(store_name, fallback)
        return _read_optional_str(env, key, store_default)


load_dotenv(ENV_FILE)
app_config = AppConfig.from_env()
