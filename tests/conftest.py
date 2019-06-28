from lastfm_pg import apiconnect
from pathlib import Path
import os
import pytest
import pylast
from mastodon import Mastodon
import tweepy


@pytest.fixture
def lastfmapi():
    secrets_file = os.path.expanduser("~/.config/lastfm_pg/") + "config.ini"
    if os.path.isfile(secrets_file):
        return apiconnect.lastfmconnect()
    else:
        api_key = os.environ["LASTFM_API_KEY"]
        api_secret = os.environ["LASTFM_API_SECRET"]
        username = os.environ["LASTFM_USERNAME"]
        network = pylast.LastFMNetwork(
            api_key=api_key, api_secret=api_secret, username=username
        )
        return network


@pytest.fixture
def twitterapi():
    secrets_file = os.path.expanduser("~/.config/lastfm_pg/") + "config.ini"
    if os.path.isfile(secrets_file):
        return apiconnect.twitterconnect()
    else:
        consumer_key = os.environ["TWITTER_CONSUMER_KEY"]
        secret_key = os.environ["TWITTER_SECRET_KEY"]
        access_token = os.environ["TWITTER_ACCESS_TOKEN"]
        access_token_secret = os.environ["TWITTER_ACCESS_TOKEN_SECRET"]

        auth = tweepy.OAuthHandler(consumer_key, secret_key)
        auth.set_access_token(access_token, access_token_secret)
        return tweepy.API(auth)


# @pytest.fixture
# def mastodonapi():
#     secrets_file = os.path.expanduser("~/.config/lastfm_pg/") + "config.ini"
#     if os.path.isfile(secrets_file):
#         return apiconnect.mastodonconnect()
#     else:
#         if not Path("mastodon_clientcred.secret").is_file():
#             Mastodon.create_app(
#                 "mastodon_bot_lastfm_pg",
#                 api_base_url=os.environ["MASTODON_API_BASE_URL"],
#                 to_file="mastodon_clientcred.secret",
#             )
#
#         if not Path("mastodon_usercred.secret").is_file():
#             mastodon = Mastodon(
#                 client_id="mastodon_clientcred.secret",
#                 api_base_url=os.environ["MASTODON_API_BASE_URL"],
#             )
#             mastodon.log_in(
#                 os.environ["MASTODON_LOGIN_EMAIL"],
#                 os.environ["MASTODON_PASSWORD"],
#                 to_file="mastodon_usercred.secret",
#             )
#
#         mastodon = Mastodon(
#             access_token="mastodon_usercred.secret",
#             api_base_url=os.environ["MASTODON_API_BASE_URL"],
#         )
#         return mastodon
