"""
lastfm playlist generator : generate playlist based on most played favorites
                            tracks of a lastfm user for a certain timeframe
"""
import logging
import argparse
import datetime
from pathlib import Path
from .utils import (
    create_list_tweets,
    upload_list_tweets,
    get_lastfm_playlist,
    return_title_playlist,
    export_playlist,
    format_playlist,
)
from .apiconnect import lastfmconnect, check_config, get_lastfm_username

logger = logging.getLogger()
logging.getLogger("pylast").setLevel(logging.WARNING)
begin_time = datetime.datetime.now()

# Need to be changed
USERNAME = "d_beley"
PLAYLIST_LENGTH = 10
TIMEFRAME_VALUES = ["7day", "1month", "3month", "6month", "12month", "overall"]
SUPPORTED_SOCIAL_MEDIA = ["twitter", "mastodon"]


def main():
    args = parse_args()
    # create sample config file
    check_config()
    network = lastfmconnect()
    social_media = args.social_media.lower()
    if args.no_upload:
        logger.debug("No upload mode activated.")
    else:
        if social_media not in SUPPORTED_SOCIAL_MEDIA:
            logger.error("%s not supported. Exiting.", social_media)
            exit()
    if args.timeframe not in TIMEFRAME_VALUES:
        logger.error(
            "Incorrect value %s for timeframe. Accepted values : %s.",
            args.columns,
            TIMEFRAME_VALUES,
        )
        exit()

    if args.username:
        try:
            username = args.username
            user = network.get_user(username)
        except Exception as e:
            logger.error("Error : %s.", e)
            exit()
    else:
        username = get_lastfm_username(network)
        user = network.get_user(username)

    playlist_tracks = get_lastfm_playlist(user, args.timeframe)

    Path("Exports").mkdir(parents=True, exist_ok=True)
    export_playlist(playlist_tracks, begin_time, args.timeframe, social_media)

    title = return_title_playlist(begin_time, args.timeframe)

    # Format playlist "index - artist - title"
    list_message = format_playlist(playlist_tracks, title)

    # Create list of tweets complying with the max length of a social media
    list_tweet = create_list_tweets(list_message, social_media)
    if not args.no_upload:
        upload_list_tweets(list_tweet, social_media)


def parse_args():
    custom_format = "%(levelname)s :: %(message)s"
    parser = argparse.ArgumentParser(
        description="Generate playlist of a user's favorite most played tracks\
                for the last week and post it to twitter or mastodon."
    )
    parser.add_argument(
        "--debug",
        help="Display debugging information",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.INFO,
    )
    parser.add_argument(
        "--username",
        "-u",
        help="Lastfm username (default : username section of the config.ini file).",
        type=str,
    )
    parser.add_argument(
        "--no_upload",
        help="Disable the upload. Use it for debugging.",
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
    logging.basicConfig(level=args.loglevel, format=custom_format)
    return args


if __name__ == "__main__":
    main()
