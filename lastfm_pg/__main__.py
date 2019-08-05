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
from .apiconnect import (
    lastfmconnect,
    check_config,
    get_lastfm_username,
    twitterconnect,
    get_twitter_username,
)

logger = logging.getLogger()
logging.getLogger("pylast").setLevel(logging.WARNING)
begin_time = datetime.datetime.now()

TIMEFRAME_VALUES = ["7day", "1month", "3month", "6month", "12month", "overall"]
SUPPORTED_SOCIAL_MEDIA = ["twitter", "mastodon"]


def main():
    args = parse_args()
    # create sample config file
    check_config(args.config_file)

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
        list_users = args.username.split(",")
    else:
        username = [get_lastfm_username(network)]
        user = network.get_user(username)

    for user in list_users:
        user = network.get_user(user)
        playlist_tracks = get_lastfm_playlist(
            user, args.timeframe, args.only_favorites
        )

        Path("Exports").mkdir(parents=True, exist_ok=True)
        export_playlist(
            playlist_tracks, begin_time, args.timeframe, social_media, user
        )

        title = return_title_playlist(
            begin_time, user, args.timeframe, args.template_file
        )

        # Format playlist "index: artist - title (playcount)"
        list_message = format_playlist(playlist_tracks, title)

        # Create list of tweets complying with the max length of a social media
        if social_media == "twitter":
            api = twitterconnect()
            twitter_username = get_twitter_username(api)
            list_tweets = create_list_tweets(
                list_message, social_media, args.hashtag, twitter_username
            )
        else:
            list_tweets = create_list_tweets(
                list_message, social_media, args.hashtag
            )

        if not args.no_upload:
            upload_list_tweets(list_tweets, social_media)


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
        help="Lastfm usernames, separated by comma (default : username section of the config.ini file).",
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
        help="Social media where the playlist will be posted (twitter or mastodon. Default : twitter).",
        type=str,
        default="twitter",
    )
    parser.add_argument(
        "--not-only-favorites",
        "-n",
        help="The playlist will be composed of any tracks, not only favorite tracks.",
        dest="only_favorites",
        action="store_false",
    )
    parser.add_argument(
        "--config_file",
        help="Path to the config file (Default : '~/.config/lastfm_pg/config.ini').",
        type=str,
        default="~/.config/lastfm_pg/config.ini",
    )
    parser.add_argument(
        "--template_file",
        help="Path to the template file for the tweet (Default : 'tweet_template.txt').",
        type=str,
        default="tweet_template.txt",
    )
    parser.add_argument(
        "--hashtag",
        help="Hashtag to insert at the end of each secondary tweets (Default : '#lastfm').",
        type=str,
        default="#lastfm",
    )
    parser.set_defaults(no_upload=False, only_favorites=True)
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel, format=custom_format)
    return args


if __name__ == "__main__":
    main()
