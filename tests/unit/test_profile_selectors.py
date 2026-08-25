from linkedin_jobs_scraper.strategies.authenticated_strategy import ProfileSelectors


def test_profile_name_supports_sdui_and_legacy_markup():
    assert '[id$="Topcard"] h2' in ProfileSelectors.name
    assert 'main h1' in ProfileSelectors.name


def test_profile_sections_use_stable_sdui_test_ids_with_legacy_fallbacks():
    assert 'profile_ExperienceTopLevelSection_' in ProfileSelectors.experience
    assert 'section:has(#experience)' in ProfileSelectors.experience
    assert 'profile_EducationTopLevelSection_' in ProfileSelectors.education
    assert 'section:has(#education)' in ProfileSelectors.education


def test_profile_avatar_supports_sdui_semantics_and_legacy_classes():
    assert '[aria-label="Profile photo"] img' in ProfileSelectors.avatar
    assert 'pv-top-card-profile-picture__image--show' in ProfileSelectors.avatar
