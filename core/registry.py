SCRAPER_REGISTRY = {}


def register_scraper(name):
    def decorator(scraper_class):
        SCRAPER_REGISTRY[name] = scraper_class
        return scraper_class

    return decorator


def get_scraper_class(name):
    return SCRAPER_REGISTRY[name]


def list_scrapers():
    return sorted(SCRAPER_REGISTRY)
