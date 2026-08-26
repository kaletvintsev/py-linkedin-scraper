from enum import Enum
from typing import NamedTuple
from typing import List


class Events(Enum):
    DATA = 'scraper:data'
    METRICS = 'scraper:metrics'
    BEGIN = 'scraper:begin'
    END = 'scraper:end'
    ERROR = 'scraper:error'
    INVALID_SESSION = 'scraper:invalid-session'
    SESSION_REFRESHED = 'scraper:session-refreshed'
    NOT_FOUND = 'scraper:not-found'
    PROFILE = 'scraper:profile'
    PROFILE_NOT_FOUND = 'scraper:profile-not-found'
    POST = 'scraper:post'


class EventSession(NamedTuple):
    """Carries a session cookie that differs from the one the scraper was given.

    Emitted so that a caller with no persistent Chrome profile, typically running in an
    ephemeral container, can store the cookie itself instead of harvesting a new one by
    hand on the next run.
    """

    li_at: str = ''


class EventBegin(NamedTuple):
    """Emitted once per query/location before scraping starts, carrying LinkedIn's
    approximate total result count (-1 when it could not be parsed)."""
    job_total: int = -1


class EventNotFound(NamedTuple):
    """Emitted when a single-job scrape targets a job that does not exist or is no longer
    available."""
    job_id: str = ''


class EventProfileNotFound(NamedTuple):
    """Emitted when a requested public LinkedIn profile cannot be found."""
    public_id: str = ''


class ProfileData(NamedTuple):
    """Public fields extracted from a LinkedIn member profile."""
    public_id: str = ''
    link: str = ''
    name: str = ''
    headline: str = ''
    location: str = ''
    about: str = ''
    avatar_url: str = ''
    current_company: str = ''
    experience: List[str] = []
    education: List[str] = []


class ReposterData(NamedTuple):
    """Public identity of a member who reposted a post."""
    name: str = ''
    profile_link: str = ''
    avatar_url: str = ''


class PostData(NamedTuple):
    """Public fields extracted from a member activity page or post search."""
    post_id: str = ''
    link: str = ''
    author_name: str = ''
    author_link: str = ''
    text: str = ''
    date_text: str = ''
    reactions: int = 0
    comments: int = 0
    reposts: int = 0
    image_urls: List[str] = []
    reposters: List[ReposterData] = []


class EventData(NamedTuple):
    query: str = ''
    location: str = ''
    job_id: str = ''
    job_index: int = -1  # Only for debug
    link: str = ''
    apply_link: str = ''
    title: str = ''
    company: str = ''
    company_link: str = ''
    company_employee_count: str = ''
    company_img_link: str = ''
    place: str = ''
    description: str = ''
    description_html: str = ''
    date: str = ''
    date_text: str = ''
    insights: List[str] = []
    salary: str = ''
    is_easy_apply: bool = False
    applicant_count: str = ''
    benefits: List[str] = []
    reposted: bool = False


class EventMetrics:
    def __init__(self):
        self.processed = 0  # Number of successfully processed jobs
        self.failed = 0  # Number of jobs failed to process
        self.missed = 0  # Number of missed jobs to load during scraping
        self.skipped = 0  # Number of skipped jobs
        self.throttled = 0  # Number of times LinkedIn answered with a 429
        self.pace = 0.0  # Seconds currently slept between jobs

    def __str__(self):
        return f'{{ processed: {self.processed}, failed: {self.failed}, missed: {self.missed}, ' \
               f'skipped: {self.skipped}, throttled: {self.throttled}, pace: {self.pace} }}'
