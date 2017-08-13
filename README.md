### Gistodon: Gist-based "toot longer" desktop app for Mastodon

500 characters is a lot more than 140, but not by *much*.
It's also unformatted text. Gistodon lets you create a [gist](https://gist.github.com) and toot a summary and a link to it.

**Note:** you need to [setup](#installing) gistodon before you can use it.

#### Tooting from the command line

For a summary of command line options: `./gistodon.py -h`.

Gistodon reads markdown text from stdin, creates a gist with that
content, and toots about it. For example:

```sh
$ ./gistodon.sh --re https://mastodon.social/users/Gargron/updates/4070304 << TOOTIT
Peter Gabriel's "[**Not one of us**](https://www.youtube.com/watch?v=dbwQ0Wy3ljQ)" begins with some mighty fine #awoo calls.
I hope you like it, @Gargron@mastodon.social 

[![Awoo](https://openclipart.org/image/300px/svg_to_png/258983/1471488955.png)](https://openclipart.org/detail/258983/howling-wolf-refixed)
TOOTIT
```

This would create a gist like [this one](https://gist.github.com/anonymous/6815766cb31e382f8b44370ef004b842#file-toot-md), and a [toot](https://social.weho.st/@thedod/960590) about it, where:

* The toot contains:
  * A plaintext excerpt from the gist.
  * A link to the gist.
  * [If needed], all mentions that appear on the gist
    (unless they're alredy in the excerpt).
* The gist linkfies all mentions and hashtags. 

Of course, `./gistodon.sh -t "Not for the meek" < /tmp/somepost.md` or `myscript | /path/to/gistodon.sh` are probably more practical ways of doing this, but the easiest way is via the `localhost` web interface.

#### Using the web interface

The simplest way to use Gistodon is by running `./gistodon.sh -w` and browsing to `http://localhost:8008`, where you'll see something like:

![Gistodon's web inteface](https://lut.im/3e96v9tevA/RsO2PJP5fCpC5eBQ.gif)

* You can autocomplete mentions and/or hashtags.
* You can paste an "in reply to" toot url. This would:
  * Show that toot's content (for reference, copy/paste, etc.).
  * If that toot has a content warning, paste it into the reply's CW field.
  * Paste that toot's author into the autocomplete field.
    (so that you can choose where to insert it into the reply's content).
* An editor button to toggle text direction between `ltr` and `rtl`.
  Note that his is a gist-wide setting:
  the gist gets wrapped in an `rtl` div if needed.

#### Installing

1. Run `./install.sh`
2. Run `./register.sh myinstance.org mymail@example.org` (you'll be prompted for a password). For command-line options, run `./register.sh -h`.

#### Multiple accounts

You can run `./register.sh` again with some other account (either on the same instance or not).
* If you do that, you might need to specify `--instance` and `--email` to `./gistodon.sh`.
* If you don't &mdash; the first account in the first instance (in an arbitrary-but-consistent order) gets selected.
* If you only supply the instance, e.g. `./gistodon.py -i otherinstance.org < somefile`, the first account (in an arbitrary-but-consistent order) on that instance will be used (i.e. if you've only registered a single account there, no need to say which).

Also note that if you use a custom app name `-a` arg at `register.sh`, you'll always need to specify `-a` when calling `gistodon.sh`

### Credits

Code is based on

* [Mastodon](https://github.com/tootsuite/mastodon/) and [Mastodon.py](https://github.com/halcy/Mastodon.py).
* [Github API](https://developer.github.com/v3/gists/).
* [Flask](http://flask.pocoo.org/) python web framework.
* [Simplemde](https://simplemde.com/) markdown editor.
* Xdsoft autocomplete [jquery](https://jquery.com/) [plugin](https://www.xdsoft.net/jqplugins/autocomplete/).
* [Fontawesome](http://fontawesome.io/) icons.

Thanks, y'all.
