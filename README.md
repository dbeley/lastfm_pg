# lastfm_pg : lastfm playlist generator

Generate playlist of a user's favorite most played tracks for the last week and post it to twitter.

This utility needs a valid config file with your lastfm API keys (get them at https://www.last.fm/api) in ~/.config/lastfm_pg/config.ini (see config_sample.ini for an example).

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
