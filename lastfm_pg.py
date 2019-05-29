"""
lastfm playlist generator : generate playlist based on you most played favorites tracks for the last week
"""
import logging
import argparse
import configparser
import os
import random
import datetime
import pylast
import tweepy
from collections import defaultdict

logger = logging.getLogger()
logging.getLogger("pylast").setLevel(logging.WARNING)
begin_time = datetime.datetime.now()
PLAYLIST_LENGTH = 10
TWITTER_MAX_CHARACTERS = 280


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
    # Need to extract all loved tracks, get_userloved doesn't seems to work
    logger.info("Getting all loved tracks for user %s", users[0])
    loved_tracks = user.get_loved_tracks(limit=None)
    loved_tracks = [x.track for x in loved_tracks]

    # List of recently played tracks
    logger.info("Getting top tracks for the last week for user %s", users[0])
    top_week_tracks = user.get_top_tracks(period="7day", limit=1000)

    # List of tracks presents in both lists
    playlist_potential_tracks = [
        (x.weight, x.item) for x in top_week_tracks if x.item in loved_tracks
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

    for index, track in enumerate(playlist_tracks, 1):
        logger.info(
            "%s: %s - %s", str(index).zfill(2), track.artist, track.title
        )

    start = begin_time - datetime.timedelta(days=begin_time.weekday())
    time = start + datetime.timedelta(days=6)

    # Creating a message complying with twitter character's limit
    headers_message = [
        f"My most played favorites tracks on #lastfm for the week of {time.strftime('%B %d %Y')}",
        "Made with https://github.com/dbeley/lastfm_pg",
    ]
    len_headers_message = sum([len(x) for x in headers_message])
    remaining_char = TWITTER_MAX_CHARACTERS - len_headers_message
    list_message = []
    for index, track in enumerate(playlist_tracks, 1):
        track_name = f"{index}: {track.artist} - {track.title}"
        logger.debug("len track_name : %s", len(track_name))
        if remaining_char - len(track_name) >= 0:
            logger.debug("Append smth")
            list_message.append(
                f"{str(index).zfill(2)}: {track.artist} - {track.title}"
            )
        else:
            logger.debug("break")
            break
        logger.debug("remaining : %s", remaining_char)
        remaining_char -= len(track_name)

    list_message.insert(0, headers_message[0])
    list_message.append(headers_message[1])
    message = "\n".join(list_message)
    logger.debug("Message to post (%s characters):", len(message))
    logger.debug(message)

    if args.no_upload_twitter:
        logger.info("No posting mode activated.")
    else:
        tweet_message(api, message)


def parse_args():
    format = "%(levelname)s :: %(message)s"
    parser = argparse.ArgumentParser(
        description="Generate playlist of a user's favorite most played tracks for the last week and post it to twitter."
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
    parser.set_defaults(no_upload_twitter=False)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel, format=format)
    return args


if __name__ == "__main__":
    main()
