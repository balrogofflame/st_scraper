from core.http import build_headers
from core.registry import register_scraper
from scrapers.families.shopline_json import ShoplineJsonScraper


@register_scraper('playjoy')
class PlayjoyScraper(ShoplineJsonScraper):
    store_name = 'playjoy'
    display_name = 'Play & Joy'
    base_url = 'https://shop.playjoylube.com/'
    home_url = f'{base_url}zh-TW'
    output_file = 'playjoy.csv'
    headers = build_headers('zh-TW,zh-Hant;q=0.9,en-US;q=0.8,en;q=0.7')
    max_pages = 100
    timeout = 10
    delay = 1
    products_per_page = 24
