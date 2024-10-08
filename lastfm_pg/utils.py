import logging
import random
import datetime
from collections import defaultdict
from .apiconnect import mastodonconnect

logger = logging.getLogger(__name__)
MASTODON_MAX_CHARACTERS = 500


def get_lastfm_playlist(user, timeframe, playlist_size, only_favorites=True):
    # List of recently played tracks
    logger.info("Getting top tracks for timeframe %s for user %s.", timeframe, user)
    top_tracks = user.get_top_tracks(period=timeframe, limit=1000)
    if only_favorites:
        # List of all loved tracks
        # Need to extract all loved tracks, get_userloved() function doesn't seems to work
        logger.info("Getting all loved tracks for user %s.", user)
        loved_tracks = user.get_loved_tracks(limit=None)
        loved_tracks = [x.track for x in loved_tracks]

        # List of tracks presents in both lists
        playlist_potential_tracks = [
            (x.weight, x.item) for x in top_tracks if x.item in loved_tracks
        ]
    else:
        # List of tracks presents in both lists
        playlist_potential_tracks = [(x.weight, x.item) for x in top_tracks]

    # dict where keys : weight, values : list of tracks
    dd_tracks = defaultdict(list)
    for track in playlist_potential_tracks:
        dd_tracks[track[0]].append(track[1])

    # Create final playlist
    playlist_tracks = []
    count = max(dd_tracks.keys())
    logger.info("Creating playlist.")
    while len(playlist_tracks) <= playlist_size | count >= 1:
        if len(playlist_tracks) >= playlist_size:
            break
        logger.debug("Length playlist : %s.", len(playlist_tracks))
        # randomize to not take the first item by alphabetical order
        randomized_dd_tracks = random.sample(dd_tracks[count], len(dd_tracks[count]))
        for track in randomized_dd_tracks:
            playlist_tracks.append([track, count])
            if len(playlist_tracks) >= playlist_size:
                break
        count -= 1
    return playlist_tracks

def format_playlist(playlist_tracks, title, csv=False):
    list_message = []
    if csv:
        headers_message = []
        list_message.append("position;artist;title;playcount")
    else:
        headers_message = [title]
    if csv:
        for index, track in list(enumerate(playlist_tracks, 1)):
            list_message.append(
                f"{str(index).zfill(2)};{track[0].artist};{track[0].title};{track[1]}"
            )
    else:
        # Reversed order so it goes from 10 to 1
        for index, track in reversed(list(enumerate(playlist_tracks, 1))):
            logger.debug(
                "%s: %s - %s (%s).",
                str(index).zfill(2),
                track[0].artist,
                track[0].title,
                track[1],
            )
            list_message.append(
                f"{str(index).zfill(2)}: {track[0].artist} - {track[0].title} ({track[1]} plays)"
            )
        list_message.insert(0, headers_message[0])
        return list_message
    return "\n".join(list_message)


def create_list_tweets(
    list_message, social_media, hashtag="#lastfm"):
    if social_media == "mastodon":
        max_characters = MASTODON_MAX_CHARACTERS
    iterator = iter(list_message)
    list_tweets_temp = []
    list_tweets = []
    # Cut the message by chunks of 280 or 500 characters
    while True:
        try:
            message = next(iterator)
            list_tweets_temp.append(message)
            sum_list_tweets_temp = sum([len(x) for x in list_tweets_temp])
            logger.debug("Number of characters for tweet : %s.", sum_list_tweets_temp)
            nb_char = (
                # number \n
                len(list_tweets_temp)
                # index
                + len("[10/10]")
                # hashtag
                + len(hashtag)
            )
            if sum_list_tweets_temp > max_characters - nb_char:
                logger.debug("Max number of characters reached. Creating new tweet.")
                last_message = list_tweets_temp[-1]
                del list_tweets_temp[-1]
                list_tweets.append(list_tweets_temp)
                list_tweets_temp = [last_message]
        except StopIteration:
            list_tweets.append(list_tweets_temp)
            logger.debug("Reached end of list_message.")
            break
    max_index = len(list_tweets)
    logger.debug("max_index : %s.", max_index)
    list_formatted_tweets = []
    for index, tweet in enumerate(list_tweets, 1):
        message = "\n".join(tweet)
        if max_index > 1:
            if index != 1:
                # add hashtag + index number
                list_formatted_tweets.append(
                    f"{message}\n{hashtag} [{index}/{max_index}]"
                )
            else:
                list_formatted_tweets.append(f"{message} [{index}/{max_index}]")
        else:
            # one message, no need for index nor hastag (present in the title)
            list_formatted_tweets.append(f"{message}")
    return list_formatted_tweets


def upload_list_tweets(list_messages, social_media):
    """Upload a list of messages to a social media."""
    tweet_id = None
    if social_media == "mastodon":
        api = mastodonconnect()
    for index, tweet in enumerate(list_messages, 1):
        logger.debug("Posting tweet %s.", index)
        if social_media == "mastodon":
            logger.info("Posting to mastodon.")
            if tweet_id:
                toot = api.status_post(tweet, in_reply_to_id=tweet_id)
            else:
                toot = api.status_post(tweet)
            tweet_id = toot["id"]


def export_playlist(playlist_tracks, begin_time, timeframe, social_media, user):
    """Export a playlist."""
    export_filename = return_export_filename(begin_time, timeframe, social_media, user)
    logger.info("Exporting playlist to %s.", export_filename)
    # Exporting playlist
    with open(export_filename, "w") as f:
        for index, track in reversed(list(enumerate(playlist_tracks, 1))):
            f.write(
                f"{str(index).zfill(2)}: {track[0].artist} - {track[0].title} ({track[1]} plays)\n"
            )


def return_export_filename(begin_time, timeframe, social_media, username):
    """Return the filename of an exported playlist."""
    if timeframe == "7day":
        start = begin_time - datetime.timedelta(weeks=1)
        export_filename = f"Exports/playlist_{username}_weekly_{start.strftime('%d-%m-%Y')}_{social_media}.txt"
    elif timeframe == "1month":
        start = begin_time - datetime.timedelta(weeks=1)
        export_filename = f"Exports/playlist_{username}_monthly_{begin_time.strftime('%m-%Y')}_{social_media}.txt"
    elif timeframe == "3month":
        export_filename = f"Exports/playlist_{username}_3months_{begin_time.strftime('%d-%m-%Y')}_{social_media}.txt"
    elif timeframe == "6month":
        export_filename = f"Exports/playlist_{username}_6months_{begin_time.strftime('%d-%m-%Y')}_{social_media}.txt"
    elif timeframe == "12month":
        export_filename = f"Exports/playlist_{username}_12months_{begin_time.strftime('%d-%m-%Y')}_{social_media}.txt"
    elif timeframe == "overall":
        export_filename = f"Exports/playlist_{username}_overall_{begin_time.strftime('%d-%m-%Y')}_{social_media}.txt"
    return export_filename


def return_title_playlist(
    begin_time, username, timeframe, template_file="tweet_template.txt"
):
    """Return the title of playlist."""

    # Change username for specific lastfm accounts
    username = str(username)
    if username == "FIPdirect":
        username = "FIP"
    elif username == "FIProck":
        username = "FIP Rock"
    elif username == "FIPjazz":
        username = "FIP Jazz"
    elif username == "FIPgroove":
        username = "FIP Groove"
    elif username == "FIPmonde":
        username = "FIP Monde"
    elif username == "FIPnouveautes":
        username = "FIP Nouveautés"
    elif username == "FIPreggae":
        username = "FIP Reggae"
    elif username == "FIPelectro":
        username = "FIP Electro"
    elif username == "FIPmetal":
        username = "FIP Metal"

    with open(template_file, "r") as f:
        tweet_template = f.read()
    if timeframe == "7day":
        start = begin_time - datetime.timedelta(weeks=1)
        timeframe = f"for the week of {start.strftime('%B %d %Y')}"
    elif timeframe == "1month":
        start = begin_time - datetime.timedelta(weeks=1)
        timeframe = f"for {start.strftime('%B %Y')}"
    elif timeframe == "3month":
        timeframe = f"for the last 3 months"
    elif timeframe == "6month":
        timeframe = f"for the last 6 months"
    elif timeframe == "12month":
        start = begin_time - datetime.timedelta(weeks=1)
        timeframe = f"for the year {start.strftime('%Y')}"
    elif timeframe == "overall":
        timeframe = f"ever"
    title = eval(tweet_template)
    return title
