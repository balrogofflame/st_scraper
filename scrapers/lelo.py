from core.registry import register_scraper
from scrapers.families.sitemap_jsonld import SitemapJsonLdScraper


@register_scraper('lelo')
class LeloScraper(SitemapJsonLdScraper):
    store_name = 'lelo'
    display_name = 'LELO'
    base_url = 'https://www.lelo.com/zh-hans'
    sitemap_url = 'https://www.lelo.com/sitemap.xml'
    output_file = 'lelo.csv'

    def extract_product_urls_from_sitemap(self, root):
        product_urls = []
        seen_urls = set()

        for url_node in self.iter_elements(root, 'url'):
            for link in list(url_node):
                hreflang = link.attrib.get('hreflang')
                href = (link.attrib.get('href') or '').strip()

                if (
                    hreflang == 'zh-hans'
                    and href.startswith(self.base_url)
                    and href not in seen_urls
                ):
                    seen_urls.add(href)
                    product_urls.append(href)
                    break

        return product_urls
