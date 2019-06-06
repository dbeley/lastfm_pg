"""
lastfm playlist generator : generate playlist based on you most played\
        favorites tracks for a certain timeframe
"""
import logging
import argparse
import configparser
import random
import datetime
import pylast
import tweepy
from mastodon import Mastodon
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger()
logging.getLogger("pylast").setLevel(logging.WARNING)
begin_time = datetime.datetime.now()

config = configparser.ConfigParser()
# same directory as the script
config.read("config.ini")

PLAYLIST_LENGTH = 10
TWITTER_MAX_CHARACTERS = 280
MASTODON_MAX_CHARACTERS = 500
TIMEFRAME_VALUES = ["7day", "1month", "3month", "6month", "12month", "overall"]
SUPPORTED_SOCIAL_MEDIA = ["twitter", "mastodon"]


def twitterconnect():
    consumer_key = config["twitter"]["consumer_key"]
    secret_key = config["twitter"]["secret_key"]
    access_token = config["twitter"]["access_token"]
    access_token_secret = config["twitter"]["access_token_secret"]

    auth = tweepy.OAuthHandler(consumer_key, secret_key)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth)


def mastodonconnect():
    if not Path("mastodon_clientcred.secret").is_file():
        Mastodon.create_app(
            "mastodon_bot_lastfm_cg",
            api_base_url=config["mastodon"]["api_base_url"],
            to_file="mastodon_clientcred.secret",
        )

    if not Path("mastodon_usercred.secret").is_file():
        mastodon = Mastodon(
            client_id="mastodon_clientcred.secret",
            api_base_url=config["mastodon"]["api_base_url"],
        )
        mastodon.log_in(
            config["mastodon"]["login_email"],
            config["mastodon"]["password"],
            to_file="mastodon_usercred.secret",
        )

    mastodon = Mastodon(
        access_token="mastodon_usercred.secret",
        api_base_url=config["mastodon"]["api_base_url"],
    )
    return mastodon


def tweet_list_message(api, list_message, social_media):
    if social_media == "mastodon":
        max_characters = MASTODON_MAX_CHARACTERS
    elif social_media == "twitter":
        max_characters = TWITTER_MAX_CHARACTERS
    iterator = iter(list_message)
    list_tweets_temp = []
    list_tweets = []
    # Cut the message by chunks of 280 characters
    while True:
        try:
            message = next(iterator)
            list_tweets_temp.append(message)
            sum_list_tweets_temp = sum([len(x) for x in list_tweets_temp])
            logger.debug(
                "Number of characters for tweet : %s.", sum_list_tweets_temp
            )
            nb_char = len(list_tweets_temp) + 6
            if sum_list_tweets_temp > max_characters - nb_char:
                logger.debug(
                    "Max number of characters reached. Creating new tweet."
                )
                last_message = list_tweets_temp[-1]
                del list_tweets_temp[-1]
                list_tweets.append(list_tweets_temp)
                list_tweets_temp = [last_message]
        except StopIteration:
            list_tweets.append(list_tweets_temp)
            logger.debug("Reached end of list_message.")
            break
    max_index = len(list_tweets)
    logger.debug("max_index : %s", max_index)
    list_formatted_tweets = []
    for index, tweet in enumerate(list_tweets, 1):
        message = "\n".join(tweet)
        if max_index > 1:
            list_formatted_tweets.append(f"{message} [{index}/{max_index}]")
        else:
            list_formatted_tweets.append(f"{message}")

    for index, tweet in enumerate(list_formatted_tweets, 1):
        logger.debug("Posting tweet %s", index)
        if social_media == "mastodon":
            api.status_post(tweet)
        elif social_media == "twitter":
            api.update_status(status=tweet)


def lastfmconnect():
    config = configparser.ConfigParser()
    # same directory as the script
    config.read("config.ini")
    api_key = config["lastfm"]["api_key"]
    api_secret = config["lastfm"]["api_secret"]

    network = pylast.LastFMNetwork(api_key=api_key, api_secret=api_secret)
    return network


def main():
    args = parse_args()
    network = lastfmconnect()
    social_media = args.social_media.lower()
    if args.no_upload:
        logger.debug("No upload mode activated.")
    else:
        if social_media not in SUPPORTED_SOCIAL_MEDIA:
            logger.error(
                "Social media %s not supported. Exiting.", social_media
            )
            exit()
        elif social_media == "twitter":
            api = twitterconnect()
        elif social_media == "mastodon":
            api = mastodonconnect()
    if args.timeframe not in TIMEFRAME_VALUES:
        logger.error(
            "Incorrect value %s for timeframe. Accepted values : %s",
            args.columns,
            TIMEFRAME_VALUES,
        )
        exit()

    if args.username:
        try:
            users = [x.strip() for x in args.username.split(",")]
            user = network.get_user(users[0])
        except Exception as e:
            logger.error("Error : %s", e)
            exit()
    else:
        logger.error("Use the -u/--username flag to set an username.")
        exit()

    # List of all loved tracks
    # Need to extract all loved tracks, get_userloved() function doesn't seems to work
    logger.info("Getting all loved tracks for user %s", users[0])
    loved_tracks = user.get_loved_tracks(limit=None)
    loved_tracks = [x.track for x in loved_tracks]

    # List of recently played tracks
    logger.info(
        "Getting top tracks for timeframe %s for user %s",
        args.timeframe,
        users[0],
    )
    top_tracks = user.get_top_tracks(period=args.timeframe, limit=1000)

    # List of tracks presents in both lists
    playlist_potential_tracks = [
        (x.weight, x.item) for x in top_tracks if x.item in loved_tracks
    ]

    # dict where keys : weight, values : list of tracks
    dd_tracks = defaultdict(list)
    for track in playlist_potential_tracks:
        dd_tracks[track[0]].append(track[1])

    # Create final playlist
    playlist_tracks = []
    count = max(dd_tracks.keys())
    logger.debug("Creating playlist")
    while len(playlist_tracks) <= PLAYLIST_LENGTH | count >= 1:
        if len(playlist_tracks) >= PLAYLIST_LENGTH:
            break
        logger.debug("Length playlist : %s", len(playlist_tracks))
        # randomize to not take the first item by alphabetical order
        randomized_dd_tracks = random.sample(
            dd_tracks[count], len(dd_tracks[count])
        )
        for track in randomized_dd_tracks:
            playlist_tracks.append(track)
            if len(playlist_tracks) >= PLAYLIST_LENGTH:
                break
        count -= 1

    Path("Exports").mkdir(parents=True, exist_ok=True)
    if args.timeframe == "7day":
        start = begin_time - datetime.timedelta(days=begin_time.weekday())
        time = start + datetime.timedelta(days=6)
        title = f"My most played favorites tracks on #lastfm for the week of {time.strftime('%B %d %Y')}:"
        export_filename = f"Exports/playlist_weekly_{time.strftime('%d-%m-%Y')}_{social_media}.txt"
    elif args.timeframe == "1month":
        title = f"My most played favorites tracks on #lastfm for {begin_time.strftime('%B %Y')}."
        export_filename = f"Exports/playlist_monthly_{begin_time.strftime('%m-%Y')}_{social_media}.txt"
    elif args.timeframe == "3month":
        title = f"My most listened albums on #lastfm for the last 3 months."
        export_filename = f"Exports/playlist_3months_{begin_time.strftime('%d-%m-%Y')}_{social_media}.txt"
    elif args.timeframe == "6month":
        title = f"My most listened albums on #lastfm for the last 6 months."
        export_filename = f"Exports/playlist_6months_{begin_time.strftime('%d-%m-%Y')}_{social_media}.txt"
    elif args.timeframe == "12month":
        title = f"My most listened albums on #lastfm for the last 12 months."
        export_filename = f"Exports/playlist_12months_{begin_time.strftime('%d-%m-%Y')}_{social_media}.txt"
    elif args.timeframe == "overall":
        title = f"My most listened albums on #lastfm ever."
        export_filename = f"Exports/playlist_overall_{begin_time.strftime('%d-%m-%Y')}_{social_media}.txt"

    logger.debug(
        "timeframe : %s, title : %s, export_filename : %s",
        args.timeframe,
        title,
        export_filename,
    )

    # Exporting playlist
    with open(export_filename, "w") as f:
        for index, track in reversed(list(enumerate(playlist_tracks, 1))):
            f.write(f"{str(index).zfill(2)}: {track.artist} - {track.title}\n")

    # Creating message list
    # headers_message = [title, "Made with https://github.com/dbeley/lastfm_pg"]
    headers_message = [title, "#lastfm"]
    list_message = []
    # Reversed order so it goes from 10 to 1
    for index, track in reversed(list(enumerate(playlist_tracks, 1))):
        logger.debug(
            "%s: %s - %s", str(index).zfill(2), track.artist, track.title
        )
        list_message.append(
            f"{str(index).zfill(2)}: {track.artist} - {track.title}"
        )
    list_message.insert(0, headers_message[0])
    list_message.append(headers_message[1])

    # Upload to social media
    if not args.no_upload:
        tweet_list_message(api, list_message, social_media)


def parse_args():
    format = "%(levelname)s :: %(message)s"
    parser = argparse.ArgumentParser(
        description="Generate playlist of a user's favorite most played tracks\
                for the last week and post it to twitter."
    )
    parser.add_argument(
        "--debug",
        help="Display debugging information",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.INFO,
    )
    parser.add_argument("--username", "-u", help="Lastfm username", type=str)
    parser.add_argument(
        "--no_upload",
        help="Disable the social media upload. Use it for debugging",
        dest="no_upload",
        action="store_true",
    )
    parser.add_argument(
        "--timeframe",
        "-t",
        help="Timeframe (Accepted values : 7day, 1month,\
                              3month, 6month, 12month, overall.\
                              Default : 7day).",
        type=str,
        default="7day",
    )
    parser.add_argument(
        "--social-media",
        "-s",
        help="Social media where the playlist will be posted (twitter or mastodon. Default = twitter).",
        type=str,
        default="twitter",
    )
    parser.set_defaults(no_upload=False)
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel, format=format)
    return args


if __name__ == "__main__":
    main()
