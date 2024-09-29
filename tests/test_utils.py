from lastfm_pg import utils
import datetime

begin_time = datetime.datetime.now()


def test_create_list_tweet_simple():
    playlist = ["TRACK 1", "TRACK 2"]
    list_tweets = utils.create_list_tweets(playlist, "mastodon")
    print(list_tweets)
    if not list_tweets == ["TRACK 1\nTRACK 2"]:
        raise AssertionError()


def test_create_list_tweet_advanced():
    playlist = ["#lastfm"] + ["TRACK"] * 200
    list_tweets = utils.create_list_tweets(playlist, "mastodon")
    print(list_tweets)
    if not len(list_tweets) == 3:
        raise AssertionError()

    for i in list_tweets:
        if "#lastfm" not in i:
            raise AssertionError()


def test_return_export_filename():
    print(utils.return_export_filename(begin_time, "7day", "mastodon", "user"))
    if not utils.return_export_filename(
        begin_time, "7day", "mastodon", "user"
    ).startswith("Exports/playlist_user_weekly"):
        raise AssertionError()
    if not utils.return_export_filename(
        begin_time, "1month", "mastodon", "user"
    ).startswith("Exports/playlist_user_monthly"):
        raise AssertionError()
    if not utils.return_export_filename(
        begin_time, "3month", "mastodon", "user"
    ).startswith("Exports/playlist_user_3months"):
        raise AssertionError()
    if not utils.return_export_filename(
        begin_time, "6month", "mastodon", "user"
    ).startswith("Exports/playlist_user_6months"):
        raise AssertionError()
    if not utils.return_export_filename(
        begin_time, "12month", "mastodon", "user"
    ).startswith("Exports/playlist_user_12months"):
        raise AssertionError()
    if not utils.return_export_filename(
        begin_time, "overall", "mastodon", "user"
    ).startswith("Exports/playlist_user_overall"):
        raise AssertionError()


def test_return_title_playlist():
    if not utils.return_title_playlist(begin_time, "user", "7day").startswith(
        "My most played favorite tracks on #lastfm for the week of "
    ):
        raise AssertionError()
    if not utils.return_title_playlist(
        begin_time, "user", "1month"
    ).startswith("My most played favorite tracks on #lastfm for "):
        raise AssertionError()
    if (
        not utils.return_title_playlist(begin_time, "user", "3month")
        == "My most played favorite tracks on #lastfm for the last 3 months."
    ):
        raise AssertionError()
    if (
        not utils.return_title_playlist(begin_time, "user", "6month")
        == "My most played favorite tracks on #lastfm for the last 6 months."
    ):
        raise AssertionError()
    if not utils.return_title_playlist(
        begin_time, "user", "12month"
    ).startswith("My most played favorite tracks on #lastfm for the year "):
        raise AssertionError()
    if (
        not utils.return_title_playlist(begin_time, "user", "overall")
        == "My most played favorite tracks on #lastfm ever."
    ):
        raise AssertionError()
