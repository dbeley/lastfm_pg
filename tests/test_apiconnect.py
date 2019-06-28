from lastfm_pg import apiconnect
import pylast
import tweepy
from mastodon import Mastodon


def test_lastfmapi(lastfmapi):
    print(type(lastfmapi))

    if not isinstance(lastfmapi, pylast.LastFMNetwork):
        raise AssertionError()


def test_twitterfmapi(twitterapi):
    print(type(twitterapi))

    if not isinstance(twitterapi, tweepy.API):
        raise AssertionError()


# def test_mastodonapi(mastodonapi):
#     print(type(mastodonapi))
#
#     if not isinstance(mastodonapi, Mastodon):
#         raise AssertionError()


def test_twitterusername(twitterapi):
    if not isinstance(apiconnect.get_twitter_username(), str):
        raise AssertionError()


def test_lastfmusername(lastfmapi):
    if not isinstance(apiconnect.get_lastfm_username(), str):
        raise AssertionError()
