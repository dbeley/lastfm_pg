from lastfm_pg import utils
import datetime

begin_time = datetime.datetime.now()


def test_create_list_tweet_simple():
    playlist = ["TRACK 1", "TRACK 2"]
    list_tweets = utils.create_list_tweets(playlist, "twitter")
    print(list_tweets)
    if not list_tweets == "TRACK 1\nTRACK 2":
        raise AssertionError()


def test_return_export_filename():
    if not utils.return_export_filename(
        begin_time, "7day", "twitter"
    ).startswith("Exports/playlist_weekly"):
        raise AssertionError()
    if not utils.return_export_filename(
        begin_time, "1month", "twitter"
    ).startswith("Exports/playlist_monthly"):
        raise AssertionError()
    if not utils.return_export_filename(
        begin_time, "3month", "twitter"
    ).startswith("Exports/playlist_3months"):
        raise AssertionError()
    if not utils.return_export_filename(
        begin_time, "6month", "twitter"
    ).startswith("Exports/playlist_6months"):
        raise AssertionError()
    if not utils.return_export_filename(
        begin_time, "12month", "twitter"
    ).startswith("Exports/playlist_12months"):
        raise AssertionError()
    if not utils.return_export_filename(
        begin_time, "overall", "twitter"
    ).startswith("Exports/playlist_overall"):
        raise AssertionError()


def test_return_title_playlist():
    if not utils.return_title_playlist(begin_time, "7day").startswith(
        "My most played favorites tracks on #lastfm for the week of "
    ):
        raise AssertionError()
    if not utils.return_title_playlist(begin_time, "1month").startswith(
        "My most played favorites tracks on #lastfm for "
    ):
        raise AssertionError()
    if (
        not utils.return_title_playlist(begin_time, "3month")
        == "My most played favorites tracks on #lastfm for the last 3 months."
    ):
        raise AssertionError()
    if (
        not utils.return_title_playlist(begin_time, "6month")
        == "My most played favorites tracks on #lastfm for the last 6 months."
    ):
        raise AssertionError()
    if (
        not utils.return_title_playlist(begin_time, "12month")
        == "My most played favorites tracks on #lastfm for the last 12 months."
    ):
        raise AssertionError()
    if (
        not utils.return_title_playlist(begin_time, "overall")
        == "My most played favorites tracks on #lastfm ever."
    ):
        raise AssertionError()
