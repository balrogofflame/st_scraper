from core.http import build_headers
from core.registry import register_scraper
from scrapers.families.sitemap_jsonld import SitemapJsonLdScraper


@register_scraper('harryboy')
class HarryboyScraper(SitemapJsonLdScraper):
    store_name = 'harryboy'
    display_name = 'Harry Boy'
    base_url = 'https://www.harryboy.com.tw/'
    sitemap_url = f'{base_url}Sitemap/sitemap_ShopSalePage.xml.gz'
    sitemap_is_gzipped = True
    output_file = 'harryboy.csv'
    headers = build_headers('zh-TW,zh-Hant;q=0.9,en-US;q=0.8,en;q=0.7')
    timeout = 10
    delay = 0.2

    def extract_product_urls_from_sitemap(self, root):
        product_urls = []

        for loc in self.iter_elements(root, 'loc'):
            href = (loc.text or '').strip()

            if href.startswith(f'{self.base_url}SalePage/Index/'):
                product_urls.append(href)

        return product_urls
