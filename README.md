autopost
========

[![CI](https://github.com/woodruffw/autopost/actions/workflows/ci.yml/badge.svg)](https://github.com/woodruffw/autopost/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/autopost.svg)](https://pypi.org/project/autopost)

A social media auto-poster for a blog.

Supported sites:

* Twitter (currently untested)
* Mastodon (any instance)
* Reddit (any subreddit)
* Bluesky

## Installation

`autopost` requires Python 3.11 or newer, and is available on PyPI:

```bash
python -m pip install autopost
```

## Usage

```console
usage: autopost [-h] [-V] [-v] [--dry-run] [--config-file CONFIG_FILE] {manual,atom} ...

auto-posts social media updates

positional arguments:
  {manual,atom}
    manual              auto-post manually
    atom                auto-post from an Atom RSS feed

options:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  -v, --verbose         be more verbose while running (default: False)
  --dry-run             perform a dry-run (default: False)
  --config-file CONFIG_FILE
                        the file to load for configuration (default: ./autopost.toml)
```

## Examples

To do anything meaningful with `autopost`, you'll need to configure
it. See [autopost.example.toml](./autopost.example.toml) for an example configuration file.

Once configured, you can use `autopost` to make a post manually:

```console
$ autopost manual "test" --url "https://example.com" --tags foo bar
🎉 reddit:/r/enosuchblog: https://reddit.com/r/enosuchblog/comments/zldk8y/test/
🎉 mastodon:@yossarian@infosec.exchange: https://infosec.exchange/@yossarian/109509443715725349
```

...where `--tags` is optional.

Alternatively, you can use `autopost atom` to retrieve a post from an Atom-style
RSS feed:

```bash
autopost atom https://example.com/feed.xml
```

In both cases, you can pass `--dry-run` to see what `autopost` *would* post
instead of actually doing it:

```console
$ autopost --dry-run atom https://blog.yossarian.net/feed.xml
dry run: would have posted Modernizing my 1980s sound system with URL:
https://blog.yossarian.net/2022/11/07/Modernizing-my-1980s-sound-system and tags: ['howto', 'workflow', 'music']
```
