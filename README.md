# lastfm_pg : lastfm playlist generator

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/5e1070dea74c4be1a8c1e2a083b6712f)](https://app.codacy.com/app/dbeley/lastfm_pg?utm_source=github.com&utm_medium=referral&utm_content=dbeley/lastfm_pg&utm_campaign=Badge_Grade_Dashboard)

Generate playlist of a user's favorite most played tracks for a certain timespan and post it to twitter or mastodon.

This utility needs a valid config file with your lastfm API keys (get them at [last.fm/api](https://www.last.fm/api).), twitter API keys (get them at [developer.twitter.com](https://developer.twitter.com).) and mastodon account information in the ~/.config/lastfm_pg/config.ini file (see config_sample.ini for an example).

Running the script for the first time will generate a sample config file if one doesn't exist yet.

In order to run the script at a given time, some systemd services are provided in the systemd-service directory. You will have to change them to match your configuration, more specifically the WorkingDirectory and ExecStart directive.

## Requirements

- pylast
- tweepy
- Mastodon.py

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
usage: lastfm_pg [-h] [--debug] [--username USERNAME] [--no_upload]
                 [--timeframe TIMEFRAME] [--social-media SOCIAL_MEDIA]
                 [--not-only-favorites] [--config_file CONFIG_FILE]
                 [--template_file TEMPLATE_FILE]

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
                        (twitter or mastodon. Default = twitter).
  --not-only-favorites, -n
                        The playlist will be composed of any tracks, not only
                        favorite tracks.
  --config_file CONFIG_FILE
                        Path to the config file (Default =
                        '~/.config/lastfm_pg/config.ini').
  --template_file TEMPLATE_FILE
                        Path to the template file for the tweet (Default =
                        'tweet_template.txt').
```

## Systemd service

```
cp systemd-service/* ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now twitter_lastfm_pg_weekly.timer
``` 

## Template

The posted tweets will follow the template. See the tweet_template.txt file for an example.

Available variables :

- timeframe
- username
