### Gistodon: "toot longer" desktop app for Mastodon

500 characters is a lot more than 140, but not by *much*.
It's also unformatted text.

Gistodon reads from markdown text from stdin and treats
first line as a title. It then creates a gist with that
content, and toots about it. For example:

```sh
$ ./gistodon.sh -t "Example Trumpinator speech" << TOOTIT

Here's an example output of [Trumpinator](https://gist.github.com/thedod/09918d32c8ce557d9f024d3d61fd17ca):

<blockquote>
We, the citizens of our military and law enforcement and, most importantly, we are looking only to the future. We assembled here today are issuing a new vision will govern our land. From this day forward, a new decree to be America First. Every decision on trade, on taxes, on immigration, on foreign affairs, will be protected by the same night sky, they fill their heart with the nations of the world has never seen before.
</blockquote>

This script [runs](https://social.weho.st/@thedod/852901) on @thedod@social.weho.st's router.
TOOTIT
```

This would create a gist like
[this one](https://gist.github.com/anonymous/50e2505c8839773cb2d8db56db15f848#file-toot-md),
and a [toot](https://social.weho.st/@thedod/915713) about it.

Note:

*  The `@thedod@social.weho.st` mention becomes a link in the gist,
   and appears in the toot (to make it a mastodon mention as well).
*  The `-t` (`--title`) argument is optional.
   If you skip it, the toot has no content warning (cw).

Of course, using and editor and then doing something like
`./gistodon.sh [-t "some title"] < /tmp/somepost.md` is probably a more practical way of doing this.

#### Installing

1. Run `./install.sh`
2. Run `./register.sh myinstance.org mymail@example.org` (you'll be prompted for a password)

#### Multiple accounts

You can run `./register.sh` again with some other account
(either on the same instance or not).
If you do that, you might need to specify `--instance` and `--email` to
`./gistodon.py`. If you don't &mdash; the first account in the first instance
(in alphabetical order) gets selected arbitrarily. If you only supply the instance,
e.g. `./gistodon.py -i otherinstance.org < somefile`, the first account (alphabetically)
on that instance will be used (so if you've only registered a single account there,
no need to say which).
