### Gistodon: "toot longer" desktop app for Mastodon

500 characters is a lot more than 140, but not by *much*.
It's also unformatted text.

Gistodon reads from markdown text from stdin and treats
first line as a title. It then creates a gist with that
content, and toots about it. For example:

```sh
$ ./gistodon.sh << TOOTIT
A long rant about lorem ipsum

As @thedod@social.weho.st et al have pointed out in several occasions,
[Lorem Ipsum] be like:

<blockquote>
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse dignissim et nisl id tristique. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque at nisi egestas, interdum nunc a, rutrum urna. Phasellus ultrices ligula sed pellentesque consectetur. Sed quis ligula tristique, laoreet lectus a, efficitur sem. Vivamus non leo vel eros vestibulum pellentesque. Donec sit amet sagittis purus. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas.
</blockquote>

It makes no *sense*!!!!!**1**.
TOOTIT
```

This would create a gist like [this one](https://gist.github.com/anonymous/1f9c26adb06d0f2d1a575ad174fddd27), and a [toot](https://social.weho.st/@thedod/913033) about it.
Note the the `@thedod@social.weho.st` mention becomes a link in the gist,
and appears in the toot (to make it a mastodon mention as well).

Of course, using and editor and then doing something like
`./gistodon.sh < /tmp/rant.md` is a more practical way of doing this.

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
