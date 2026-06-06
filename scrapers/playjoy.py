from core.registry import register_scraper
from scrapers.families.shopline_json import ShoplineJsonScraper


@register_scraper('playjoy')
class PlayjoyScraper(ShoplineJsonScraper):
    store_name = 'playjoy'
    display_name = 'Play & Joy'
    base_url = 'https://shop.playjoylube.com/'
    home_url = f'{base_url}zh-TW'
    output_file = 'playjoy.csv'
    products_per_page = 24
