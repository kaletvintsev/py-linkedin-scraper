from selenium import webdriver
from ..query import Query


class Strategy:
    def __init__(self, scraper: 'LinkedinScraper'):
        self.scraper = scraper

    def run(
        self,
        driver: webdriver,
        search_url: str,
        query: Query,
        location: str,
        page_offset: int
    ) -> None:
        raise NotImplementedError('Must implement method in subclass')

    def scrape_job(
        self,
        driver: webdriver,
        job_id: str,
        apply_link: bool = False
    ) -> None:
        raise NotImplementedError('Must implement method in subclass')

    def scrape_profile(self, driver: webdriver, public_id: str) -> None:
        raise NotImplementedError('Must implement method in subclass')

    def scrape_profile_posts(
        self,
        driver: webdriver,
        public_id: str,
        limit: int,
        stop_post_id: str = '',
        published_after: str = '',
    ) -> None:
        raise NotImplementedError('Must implement method in subclass')

    def scrape_post(
        self,
        driver: webdriver,
        post_url: str,
        include_reposters: bool = False,
        reposters_limit: int = 100,
    ) -> None:
        raise NotImplementedError('Must implement method in subclass')

    def search_posts(self, driver: webdriver, search_url: str, limit: int) -> None:
        raise NotImplementedError('Must implement method in subclass')
