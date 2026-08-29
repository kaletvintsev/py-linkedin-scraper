from unittest.mock import Mock

import pytest

import linkedin_jobs_scraper.linkedin_scraper as scraper_module
from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import Events, PostData
from linkedin_jobs_scraper.strategies.authenticated_strategy import EXTRACT_PROFILE_POSTS_SCRIPT


class FakeDriver:
    current_url = 'https://www.linkedin.com/feed/'

    def get_cookie(self, _name):
        return None

    def quit(self):
        self.closed = True


def test_scrape_profile_posts_passes_options_to_strategy(monkeypatch):
    driver = FakeDriver()
    monkeypatch.setattr(scraper_module, 'build_driver', lambda **_kwargs: driver)
    scraper = LinkedinScraper(headless=True, max_workers=1)
    scraper._strategy.scrape_profile_posts = Mock()

    scraper.scrape_profile_posts(
        'https://www.linkedin.com/in/%D0%B2%D0%B8%D0%BA%D1%82%D0%BE%D1%80%D0%B8%D1%8F-%D0%B7%D0%B0%D0%BA%D0%B8%D1%80%D0%BE%D0%B2%D0%B0-0499941b7/',
        limit=7,
        stop_post_id='123',
        published_after='2026-08-22',
    )

    scraper._strategy.scrape_profile_posts.assert_called_once_with(
        driver, 'виктория-закирова-0499941b7', 7, '123', '2026-08-22')
    assert driver.closed is True


@pytest.mark.parametrize('limit', [0, -1, 1.5, True, '10'])
def test_scrape_profile_posts_rejects_invalid_limit(limit):
    scraper = LinkedinScraper(headless=True, max_workers=1)

    with pytest.raises(ValueError):
        scraper.scrape_profile_posts('satya-nadella', limit=limit)


def test_post_event_accepts_one_argument_callback():
    scraper = LinkedinScraper(headless=True, max_workers=1)
    received = []
    post = PostData(post_id='123', text='Hello')

    scraper.on(Events.POST, lambda data: received.append(data))
    scraper.emit(Events.POST, post)

    assert received == [post]


@pytest.mark.parametrize(('name', 'value'), [
    ('stop_post_id', None),
    ('published_after', None),
])
def test_scrape_profile_posts_rejects_invalid_cursor_options(name, value):
    scraper = LinkedinScraper(headless=True, max_workers=1)

    with pytest.raises(ValueError):
        scraper.scrape_profile_posts('satya-nadella', **{name: value})


def test_scrape_profile_posts_rejects_invalid_date():
    scraper = LinkedinScraper(headless=True, max_workers=1)

    with pytest.raises(ValueError):
        scraper.scrape_profile_posts('satya-nadella', published_after='last week')


def test_post_extractor_uses_activity_urn_and_semantic_fallbacks():
    assert 'urn:li:activity:' in EXTRACT_PROFILE_POSTS_SCRIPT
    assert '[data-urn^="urn:li:activity:"]' in EXTRACT_PROFILE_POSTS_SCRIPT
    assert '.update-components-update-v2__commentary' in EXTRACT_PROFILE_POSTS_SCRIPT
