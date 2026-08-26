from unittest.mock import Mock, call

import pytest

import linkedin_jobs_scraper.linkedin_scraper as scraper_module
from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.strategies.authenticated_strategy import (
    EXTRACT_REPOSTERS_SCRIPT,
    EXTRACT_SEARCH_POSTS_SCRIPT,
    EXTRACT_SINGLE_POST_SCRIPT,
    OPEN_REPOSTERS_SCRIPT,
    SCROLL_REPOSTERS_SCRIPT,
)


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


@pytest.mark.parametrize('url', [
    'https://www.linkedin.com/feed/update/urn:li:activity:7497753341712789504/',
    'https://www.linkedin.com/posts/example_python-activity-7497753341712789504-abcd',
])
def test_scrape_post_passes_permalink_to_strategy(monkeypatch, url):
    driver = FakeDriver()
    monkeypatch.setattr(scraper_module, 'build_driver', lambda **_kwargs: driver)
    scraper = LinkedinScraper(headless=True, max_workers=1)
    scraper._strategy.scrape_post = Mock()

    scraper.scrape_post(url)

    scraper._strategy.scrape_post.assert_called_once_with(driver, url)
    assert driver.closed is True


@pytest.mark.parametrize('value', [
    '', 42, 'https://example.com/feed/update/urn:li:activity:1/',
    'https://www.linkedin.com/in/example/',
])
def test_scrape_post_rejects_invalid_permalink(value):
    with pytest.raises(ValueError):
        LinkedinScraper(headless=True, max_workers=1).scrape_post(value)


def test_scrape_posts_uses_one_driver_for_all_permalinks(monkeypatch):
    driver = FakeDriver()
    build_driver = Mock(return_value=driver)
    monkeypatch.setattr(scraper_module, 'build_driver', build_driver)
    scraper = LinkedinScraper(headless=True, max_workers=2)
    scraper._strategy.scrape_post = Mock()
    urls = [
        'https://www.linkedin.com/feed/update/urn:li:activity:7497753341712789504/',
        'https://www.linkedin.com/posts/example_python-activity-7497753341712789505-abcd',
    ]

    scraper.scrape_posts(urls)

    assert scraper._strategy.scrape_post.call_args_list == [
        call(driver, urls[0]),
        call(driver, urls[1]),
    ]
    build_driver.assert_called_once()
    assert driver.closed is True


def test_scrape_posts_accepts_one_string(monkeypatch):
    driver = FakeDriver()
    monkeypatch.setattr(scraper_module, 'build_driver', lambda **_kwargs: driver)
    scraper = LinkedinScraper(headless=True, max_workers=1)
    scraper._strategy.scrape_post = Mock()
    url = 'https://www.linkedin.com/feed/update/urn:li:activity:7497753341712789504/'

    scraper.scrape_posts(url)

    scraper._strategy.scrape_post.assert_called_once_with(driver, url)


def test_scrape_post_enables_reposters_with_limit(monkeypatch):
    driver = FakeDriver()
    monkeypatch.setattr(scraper_module, 'build_driver', lambda **_kwargs: driver)
    scraper = LinkedinScraper(headless=True, max_workers=1)
    scraper._strategy.scrape_post = Mock()
    url = 'https://www.linkedin.com/feed/update/urn:li:activity:7497753341712789504/'

    scraper.scrape_post(url, include_reposters=True, reposters_limit=7)

    scraper._strategy.scrape_post.assert_called_once_with(driver, url, True, 7)


@pytest.mark.parametrize(('include_reposters', 'reposters_limit'), [
    ('yes', 10), (False, 0), (False, -1), (False, True), (False, 1.5),
])
def test_scrape_post_rejects_invalid_reposter_options(include_reposters, reposters_limit):
    url = 'https://www.linkedin.com/feed/update/urn:li:activity:7497753341712789504/'
    with pytest.raises(ValueError):
        LinkedinScraper(headless=True, max_workers=1).scrape_post(
            url, include_reposters=include_reposters, reposters_limit=reposters_limit)


@pytest.mark.parametrize('value', [[], (), [None], ['https://www.linkedin.com/in/example/']])
def test_scrape_posts_rejects_invalid_collection(value):
    with pytest.raises(ValueError):
        LinkedinScraper(headless=True, max_workers=1).scrape_posts(value)


def test_single_post_extractor_supports_sdui_and_legacy_markup():
    assert '[role="listitem"]' in EXTRACT_SINGLE_POST_SCRIPT
    assert '[data-urn^="urn:li:activity:"]' in EXTRACT_SINGLE_POST_SCRIPT
    assert 'data-testid="expandable-text-box"' in EXTRACT_SINGLE_POST_SCRIPT
    assert 'activity-' in EXTRACT_SINGLE_POST_SCRIPT


def test_reposter_scripts_use_stable_sdui_semantics():
    assert 'UpdateDetail' in OPEN_REPOSTERS_SCRIPT
    assert 'reposts?' in OPEN_REPOSTERS_SCRIPT
    assert '.click()' not in OPEN_REPOSTERS_SCRIPT
    assert 'RepostList' in EXTRACT_REPOSTERS_SCRIPT
    assert '[role="listitem"]' in EXTRACT_REPOSTERS_SCRIPT
    assert 'reposted this' in EXTRACT_REPOSTERS_SCRIPT
    assert 'LazyColumn' in SCROLL_REPOSTERS_SCRIPT
