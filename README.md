# lastfm_pg : lastfm playlist generator

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/5e1070dea74c4be1a8c1e2a083b6712f)](https://app.codacy.com/app/dbeley/lastfm_pg?utm_source=github.com&utm_medium=referral&utm_content=dbeley/lastfm_pg&utm_campaign=Badge_Grade_Dashboard)

Generate playlist of a user's favorite most played tracks for the last week and post it to twitter or mastodon.

This utility needs a valid config file with your lastfm API keys (get them at [last.fm/api](https://www.last.fm/api).), twitter API keys (get them at [developer.twitter.com](https://developer.twitter.com).) and mastodon account information in the same directory as the main script (see config_sample.ini for an example).

## Requirements

  *   pylast
  *   tweepy
  *   Mastodon.py

## Installation in a virtualenv (recommended)

```
git clone https://github.com/dbeley/lastfm_pg
cd lastfm_pg
pipenv install '-e .'
```

## Usage

Show the help and the available options.

```
lastfm_pg -h
```

```
usage: lastfm_pg.py [-h] [--debug] [--username USERNAME] [--no_upload]
                    [--timeframe TIMEFRAME] [--social-media SOCIAL_MEDIA]

Generate playlist of a user's favorite most played tracks for the last week
and post it to twitter or mastodon.

optional arguments:
  -h, --help            show this help message and exit
  --debug               Display debugging information
  --username USERNAME, -u USERNAME
                        Lastfm username (default : username section of the
                        config.ini file).
  --no_upload           Disable the upload. Use it for debugging.
  --timeframe TIMEFRAME, -t TIMEFRAME
                        Timeframe (Accepted values : 7day, 1month, 3month,
                        6month, 12month, overall. Default : 7day).
  --social-media SOCIAL_MEDIA, -s SOCIAL_MEDIA
                        Social media where the playlist will be posted
                        (twitter or mastodon. Default : twitter).
```
