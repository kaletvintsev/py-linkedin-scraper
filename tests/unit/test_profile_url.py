import pytest

from linkedin_jobs_scraper.utils.url import get_profile_public_id


@pytest.mark.parametrize(('value', 'expected'), [
    ('satya-nadella', 'satya-nadella'),
    ('https://www.linkedin.com/in/satya-nadella/', 'satya-nadella'),
    ('https://linkedin.com/in/satya-nadella?trk=public_profile', 'satya-nadella'),
])
def test_get_profile_public_id(value: str, expected: str) -> None:
    assert get_profile_public_id(value) == expected


@pytest.mark.parametrize('value', [
    '',
    'https://example.com/in/satya-nadella',
    'https://www.linkedin.com/company/microsoft/',
    'https://www.linkedin.com/in/invalid%20id/',
])
def test_get_profile_public_id_rejects_unsupported_values(value: str) -> None:
    with pytest.raises(ValueError):
        get_profile_public_id(value)
