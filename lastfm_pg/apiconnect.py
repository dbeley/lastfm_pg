from pathlib import Path
import logging
import configparser
import pylast
import tweepy
import os
from mastodon import Mastodon

logger = logging.getLogger()
logging.getLogger("pylast").setLevel(logging.WARNING)

# USER_CONFIG_DIR = os.path.expanduser("~/.config/lastfm_pg/")
# CONFIG = configparser.ConfigParser()
# CONFIG.read(USER_CONFIG_DIR + "config.ini")


def check_config(config_file):
    config_file = os.path.expanduser(config_file)
    user_config_dir = os.path.expanduser("~/.config/lastfm_pg/")

    logger.debug("Checking configuration at %s.", config_file)
    if Path(config_file).is_file():
        try:
            global CONFIG
            CONFIG = configparser.ConfigParser()
            CONFIG.read(config_file)
            api_key = CONFIG["lastfm"]["api_key"]
            # config_temp = configparser.ConfigParser()
            # config_temp.read(config_file)
            # api_key = config_temp["lastfm"]["api_key"]
        except Exception as e:
            logger.error(
                (
                    "Error with the config file. Be sure to have a valid "
                    "~/.config/lastfm_pg/config.ini file. Error : %s"
                ),
                e,
            )
            exit()
    else:
        if not os.path.exists(user_config_dir):
            logger.info(
                (
                    "Configuration folder not found. "
                    "Creating ~/.config/lastfm_pg/."
                )
            )
            os.makedirs(user_config_dir)
        if not Path(config_file).is_file():
            sample_config = (
                "[lastfm]\n"
                "username=username_here\n"
                "api_key=api_key_here\n"
                "api_secret=api_secret_here\n"
                "\n"
                "[twitter]\n"
                "consumer_key=consumer_key_here\n"
                "secret_key=secret_key_here\n"
                "access_token=access_token_here\n"
                "access_token_secret=access_token_secret_here\n"
                "\n"
                "[mastodon]\n"
                "api_base_url=api_base_url_here\n"
                "login_email=login_email_here\n"
                "password=password_here\n"
            )
            with open(config_file, "w") as f:
                f.write(sample_config)
            logger.info(
                (
                    "A sample configuration file has been created at "
                    "~/.config/lastfm_pg/config.ini."
                )
            )
        exit()


def twitterconnect():
    consumer_key = CONFIG["twitter"]["consumer_key"]
    secret_key = CONFIG["twitter"]["secret_key"]
    access_token = CONFIG["twitter"]["access_token"]
    access_token_secret = CONFIG["twitter"]["access_token_secret"]

    auth = tweepy.OAuthHandler(consumer_key, secret_key)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth)


def mastodonconnect():
    if not Path("mastodon_clientcred.secret").is_file():
        Mastodon.create_app(
            "mastodon_bot_lastfm_pg",
            api_base_url=CONFIG["mastodon"]["api_base_url"],
            to_file="mastodon_clientcred.secret",
        )

    if not Path("mastodon_usercred.secret").is_file():
        mastodon = Mastodon(
            client_id="mastodon_clientcred.secret",
            api_base_url=CONFIG["mastodon"]["api_base_url"],
        )
        mastodon.log_in(
            CONFIG["mastodon"]["login_email"],
            CONFIG["mastodon"]["password"],
            to_file="mastodon_usercred.secret",
        )

    mastodon = Mastodon(
        access_token="mastodon_usercred.secret",
        api_base_url=CONFIG["mastodon"]["api_base_url"],
    )
    return mastodon


def lastfmconnect():
    api_key = CONFIG["lastfm"]["api_key"]
    api_secret = CONFIG["lastfm"]["api_secret"]
    username = CONFIG["lastfm"]["username"]

    network = pylast.LastFMNetwork(
        api_key=api_key, api_secret=api_secret, username=username
    )
    return network


def get_twitter_username(api):
    return api.me().screen_name


def get_lastfm_username(api):
    # return CONFIG["lastfm"]["username"]
    return api.username
