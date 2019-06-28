from lastfm_pg import apiconnect
import pytest


@pytest.fixture
def twitterapi():
    return apiconnect.twitterconnect()


@pytest.fixture
def lastfmapi():
    return apiconnect.lastfmconnect()


@pytest.fixture
def mastodonapi():
    return apiconnect.mastodonconnect()
