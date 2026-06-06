import unittest

from core.settings import AppConfig


class SettingsTestCase(unittest.TestCase):
    def test_from_env_reads_global_overrides(self):
        config = AppConfig.from_env({
            'SCRAPER_TIMEOUT': '25',
            'SCRAPER_DELAY': '0.5',
            'SCRAPER_MAX_PAGES': '9',
            'SCRAPER_MAX_CATEGORIES': '80',
            'EXCHANGE_RATE_TIMEOUT': '7',
            'SCRAPER_USER_AGENT': 'DemoAgent/1.0',
        })

        self.assertEqual(config.scraper_timeout, 25)
        self.assertEqual(config.scraper_delay, 0.5)
        self.assertEqual(config.scraper_max_pages, 9)
        self.assertEqual(config.scraper_max_categories, 80)
        self.assertEqual(config.exchange_rate_timeout, 7)
        self.assertEqual(config.scraper_user_agent, 'DemoAgent/1.0')

    def test_store_defaults_are_centralized(self):
        config = AppConfig.from_env({})

        self.assertEqual(config.get_scraper_delay('harryboy', environ={}), 0.2)
        self.assertEqual(config.get_scraper_max_categories('drqq', environ={}), 300)
        self.assertEqual(config.get_scraper_max_categories('sallyq', environ={}), 50)
        self.assertEqual(
            config.get_scraper_accept_language('womanizer', environ={}),
            'en-US,en;q=0.9'
        )

    def test_store_specific_env_overrides_take_priority(self):
        config = AppConfig.from_env({})
        env = {
            'SCRAPER_HARRYBOY_DELAY': '0.8',
            'SCRAPER_DRQQ_MAX_CATEGORIES': '120',
            'SCRAPER_WOMANIZER_ACCEPT_LANGUAGE': 'fr-FR,fr;q=0.9',
        }

        self.assertEqual(config.get_scraper_delay('harryboy', environ=env), 0.8)
        self.assertEqual(config.get_scraper_max_categories('drqq', environ=env), 120)
        self.assertEqual(
            config.get_scraper_accept_language('womanizer', environ=env),
            'fr-FR,fr;q=0.9'
        )


if __name__ == '__main__':
    unittest.main()
