from unittest.mock import Mock

import pytest

import linkedin_jobs_scraper.linkedin_scraper as scraper_module
from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.strategies.authenticated_strategy import EXTRACT_SEARCH_POSTS_SCRIPT


class FakeDriver:
    current_url = 'https://www.linkedin.com/feed/'

    def get_cookie(self, _name):
        return None

    def quit(self):
        self.closed = True


def test_search_posts_builds_content_search_url(monkeypatch):
    driver = FakeDriver()
    monkeypatch.setattr(scraper_module, 'build_driver', lambda **_kwargs: driver)
    scraper = LinkedinScraper(headless=True, max_workers=1)
    scraper._strategy.search_posts = Mock()

    scraper.search_posts('ищем python разработчика', limit=7)

    scraper._strategy.search_posts.assert_called_once_with(
        driver,
        'https://www.linkedin.com/search/results/content/'
        '?keywords=%D0%B8%D1%89%D0%B5%D0%BC+python+%D1%80%D0%B0%D0%B7%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D1%87%D0%B8%D0%BA%D0%B0'
        '&origin=GLOBAL_SEARCH_HEADER',
        7,
    )
    assert driver.closed is True


def test_search_posts_preserves_linkedin_content_url(monkeypatch):
    driver = FakeDriver()
    monkeypatch.setattr(scraper_module, 'build_driver', lambda **_kwargs: driver)
    scraper = LinkedinScraper(headless=True, max_workers=1)
    scraper._strategy.search_posts = Mock()
    url = 'https://www.linkedin.com/search/results/content/?keywords=python&origin=CLUSTER_EXPANSION'

    scraper.search_posts(url, limit=2)

    scraper._strategy.search_posts.assert_called_once_with(driver, url, 2)


@pytest.mark.parametrize('value', ['', '   ', 42, 'https://example.com/search/results/content/'])
def test_search_posts_rejects_invalid_query_or_url(value):
    with pytest.raises(ValueError):
        LinkedinScraper(headless=True, max_workers=1).search_posts(value)


@pytest.mark.parametrize('limit', [0, -1, 1.5, True, '10'])
def test_search_posts_rejects_invalid_limit(limit):
    with pytest.raises(ValueError):
        LinkedinScraper(headless=True, max_workers=1).search_posts('python', limit=limit)


def test_search_post_extractor_uses_sdui_semantics_not_generated_classes():
    assert 'SearchResultsContent' in EXTRACT_SEARCH_POSTS_SCRIPT
    assert '[role="listitem"]' in EXTRACT_SEARCH_POSTS_SCRIPT
    assert 'Feed post' in EXTRACT_SEARCH_POSTS_SCRIPT
    assert 'data-testid="expandable-text-box"' in EXTRACT_SEARCH_POSTS_SCRIPT
