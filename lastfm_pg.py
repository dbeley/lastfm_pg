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
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger()
logging.getLogger("pylast").setLevel(logging.WARNING)
begin_time = datetime.datetime.now()
PLAYLIST_LENGTH = 10
TWITTER_MAX_CHARACTERS = 280
TIMEFRAME_VALUES = ["7day", "1month", "3month", "6month", "12month", "overall"]


def twitterconnect():
    config = configparser.ConfigParser()
    # same directory as the script
    config.read("config.ini")
    ConsumerKey = config["twitter"]["ConsumerKey"]
    SecretKey = config["twitter"]["SecretKey"]
    AccessToken = config["twitter"]["AccessToken"]
    AccessTokenSecret = config["twitter"]["AccessTokenSecret"]

    auth = tweepy.OAuthHandler(ConsumerKey, SecretKey)
    auth.set_access_token(AccessToken, AccessTokenSecret)
    return tweepy.API(auth)


def tweet_message(api, message):
    api.update_status(status=message)


def tweet_list_message(api, list_message):
    iterator = iter(list_message)
    list_tweets_temp = []
    list_tweets = []
    while True:
        try:
            message = next(iterator)
            list_tweets_temp.append(message)
            sum_list_tweets_temp = sum([len(x) for x in list_tweets_temp])
            logger.debug(
                "Number of characters for tweet : %s.", sum_list_tweets_temp
            )
            nb_char = len(list_tweets_temp) + 6
            if sum_list_tweets_temp > TWITTER_MAX_CHARACTERS - nb_char:
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
    list_formatted_tweets = []
    for index, tweet in enumerate(list_tweets, 1):
        message = "\n".join(tweet)
        list_formatted_tweets.append(f"{message} [{index}/{max_index}]")

    for index, tweet in enumerate(list_formatted_tweets, 1):
        logger.debug("Posting tweet %s", index)
        api.update_status(status=tweet)


def lastfmconnect():
    config = configparser.ConfigParser()
    # same directory as the script
    config.read("config.ini")
    API_KEY = config["lastfm"]["API_KEY"]
    API_SECRET = config["lastfm"]["API_SECRET"]

    network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)
    return network


def main():
    args = parse_args()
    network = lastfmconnect()
    if args.no_upload_twitter:
        logger.debug("No upload to twitter.")
    else:
        logger.debug("Upload to twitter.")
        api = twitterconnect()
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

    logger.debug("Exporting playlist")
    Path("Exports").mkdir(parents=True, exist_ok=True)
    if args.timeframe == "7day":
        start = begin_time - datetime.timedelta(days=begin_time.weekday())
        time = start + datetime.timedelta(days=6)
        title = f"My most played favorites tracks on #lastfm for the week of {time.strftime('%B %d %Y')}:"
        export_filename = (
            f"Exports/playlist_weekly_{time.strftime('%d-%m-%Y')}.txt"
        )
    elif args.timeframe == "1month":
        title = f"My most played favorites tracks on #lastfm for {begin_time.strftime('%B %Y')}."
        export_filename = (
            f"Exports/playlist_monthly_{begin_time.strftime('%m-%Y')}.txt"
        )
    elif args.timeframe == "3month":
        title = f"My most listened albums on #lastfm for the last 3 months."
        export_filename = (
            f"Exports/playlist_3months_{begin_time.strftime('%d-%m-%Y')}.txt"
        )
    elif args.timeframe == "6month":
        title = f"My most listened albums on #lastfm for the last 6 months."
        export_filename = (
            f"Exports/playlist_6months_{begin_time.strftime('%d-%m-%Y')}.txt"
        )
    elif args.timeframe == "12month":
        title = f"My most listened albums on #lastfm for the last 12 months."
        export_filename = (
            f"Exports/playlist_12months_{begin_time.strftime('%d-%m-%Y')}.txt"
        )
    elif args.timeframe == "overall":
        title = f"My most listened albums on #lastfm ever."
        export_filename = (
            f"Exports/playlist_overall_{begin_time.strftime('%d-%m-%Y')}.txt"
        )

    logger.debug(
        "timeframe : %s, title : %s, export_filename : %s",
        args.timeframe,
        title,
        export_filename,
    )

    with open(export_filename, "w") as f:
        for index, track in reversed(list(enumerate(playlist_tracks, 1))):
            f.write(f"{str(index).zfill(2)}: {track.artist} - {track.title}\n")

    headers_message = [title, "Made with https://github.com/dbeley/lastfm_pg"]
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

    if args.no_upload_twitter:
        logger.info("No posting mode activated.")
    else:
        tweet_list_message(api, list_message)


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
        "--no_upload_twitter",
        help="Disable the twitter upload. Use it for debugging",
        dest="no_upload_twitter",
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
    parser.set_defaults(no_upload_twitter=False)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel, format=format)
    return args


if __name__ == "__main__":
    main()
