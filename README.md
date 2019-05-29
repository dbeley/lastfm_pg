# lastfm_pg : lastfm playlist generator

Generate playlist of a user's favorite most played tracks for the last week and post it to twitter.

This utility needs a valid config file with your lastfm API keys (get them at https://www.last.fm/api) and your twitter API keys (get them at https://developer.twitter.com) in the same directory as the main script (see config_sample.ini for an example).

## Requirements

- pylast
- tweepy

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
usage: lastfm_pg.py [-h] [--debug] [--username USERNAME] [--no_upload_twitter]

Generate playlist of a user's favorite most played tracks for the last week
and post it to twitter.

optional arguments:
  -h, --help            show this help message and exit
  --debug               Display debugging information
  --username USERNAME, -u USERNAME
                        Lastfm username
  --no_upload_twitter   Disable the twitter upload. Use it for debugging
```
