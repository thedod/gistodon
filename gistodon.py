import os, sys, re, argparse, time, json, logging
import requests
from glob import glob
from urlparse import urlsplit
from getpass import getpass
from mastodon import Mastodon
from markdown import markdown
from html_text import extract_text
from flask import (Flask, render_template, abort,
    request, redirect, jsonify)

DEBUG = False       # If it ain't broke, don't debug it.
NO_TOOTING = False  # Handy during debug: create gist, but don't toot.

RE_HASHTAG = re.compile(u'(?:^|(?<=\s))#(\\w+)')
RE_MENTION = re.compile(u'(?:^|(?<=\s))@(\\w+)@([\\w.]+)')

def get_hashtags(s, ignore=None):
    tags = set(
        ['#'+tag.lower() for tag in RE_HASHTAG.findall(s)])
    if ignore:
        tags -= get_hashtags(ignore)
    return tags

def linkify_hashtags(s, instance):
    return RE_HASHTAG.sub(
        lambda m:
            u"[#{tag}](https://{instance}/tags/{tag})".format(
                tag=m.group(1), instance=instance),
        s)

def get_mentions(s, ignore=None):
    mentions = set(
        [u"@{}@{}".format(user,instance)
         for user, instance in RE_MENTION.findall(s)])
    if ignore:
        mentions -= get_mentions(ignore)
    return mentions

def linkify_mentions(s):
    return RE_MENTION.sub(
        lambda m:
            u"[@{user}](https://{instance}/@{user})".format(
                user=m.group(1), instance=m.group(2)),
        s)

def url2toot(masto, url):
    u = urlsplit(url)
    if not (u.scheme=='https' and u.netloc and u.path):
        return None  # Don't bother the instance
    res = masto.search(url, True)
    res = res.get('statuses',[])
    return res and res[0] or None

def make_gist(title, body):
    return requests.post(
        "https://api.github.com/gists",
        json={
            "description": title,
            "public": True,
            "files": {
                "TOOT.md": {
                    "content": u"### {}\n\n{}".format(title, body)
                }
            }
        }
    ).json()['html_url']+"#file-toot-md"

def post(masto, body, instance, title=None,
         direction='ltr', in_reply_to=None):
    # Markdown more than we need, to [hopefully] discard chopped markup.
    summary = extract_text(markdown(body.strip()))[:140]
    hashtags = get_hashtags(body, ignore=summary)
    mentions = get_mentions(body, ignore=summary)
    irt_id = in_reply_to and in_reply_to.get('id') or None
    body = linkify_hashtags(linkify_mentions(body), instance)
    if direction=='rtl':
        body = u"""<div dir="rtl">
{}
</div>""".format(markdown(body))
    if in_reply_to:
        body = u"""#### In reply to [@{}]({}):

{}""".format(
        in_reply_to['account']['username'],
        in_reply_to['url'], body)
    gist = make_gist(
        title or u"A gistodon toot, {} GMT".format(
            time.asctime(time.gmtime())),
        body+u"""

###### Generated by [Gistodon](https://github.com/thedod/gistodon/#readme).""")
    if NO_TOOTING:
        return gist
    status = u'{}... {}'.format(summary, gist)
    if hashtags or mentions:
        status += u'\n'+u' '.join(hashtags.union(mentions))
    return masto.status_post(
        status, spoiler_text=title, in_reply_to_id=irt_id)['url']

def webserver(masto, instance, account):
    app = Flask(__name__, static_url_path='')
 
    @app.route('/')
    def index():
        re = request.args.get('re','')
        return render_template('index.html', account=account,
            re=re)

    @app.route('/toot', methods=['POST'])
    def tootit():
        if not request.form['markdown'].strip():
            return "Nothing to toot"
        in_reply_to=request.form.get('re')
        if in_reply_to:
            in_reply_to = url2toot(masto, in_reply_to)
            if not in_reply_to:
                abort(500, 'The "in reply to" url is not a toot.')
        return redirect(post(
            masto, request.form['markdown'], instance,
            title=request.form['title'],
            in_reply_to=in_reply_to,
            direction=request.form['direction']))

    @app.route('/re', methods=['GET', 'POST'])
    def tootsearch():
        return jsonify(url2toot(masto,
            request.form.get('q', request.args.get('q',''))))

    @app.route('/search', methods=['GET', 'POST'])
    def search():
        q = request.form.get(
            'q', request.args.get('q','')).strip()
        if not q:
            return jsonify([])
        res = masto.search(q, True)
        return jsonify(sorted(
            [
                {
                    # This trick makes sure both local and external
                    # accounts get a @hostname suffix.
                    "value": "@{}@{}".format(
                        a["username"], urlsplit(a["url"]).netloc),
                    "title": a.get("display_name")
                } for a in res.get('accounts',[])]+ \
            [{"value": '#'+a} for a in res.get('hashtags',[])],
            key=lambda s: s['value'].lower()))

    app.run(host='localhost', port=8008, debug=DEBUG)


def main():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    parser = argparse.ArgumentParser(
        description=("Toot stdin as a gist [markdown is supported],"
                     " or launch a localhost web interface."))
    parser.add_argument('-i', '--instance',
                        help='Your mastodon instance (e.g. mastodon.social).')
    parser.add_argument('-e', '--email',
                        help='The email address you login to that instance with.')
    parser.add_argument('-a', '--app_name', default='Gistodon',
                        help=('Name for the app (default is Gistodon).'
                              ' Appears below the toot, near the date.'))
    parser.add_argument('-w', '--web', action="store_true",
                        help=("Run as a web server on localhost"
                              " (toot-specific --title, --re, and --rtl"
                              " are ignored)."))
    parser.add_argument('-t', '--title',
                        help="Optional: gist's title, and the toot's content warning (CW).")
    parser.add_argument('-r', '--re',
                        help="Optional: url of the toot you're replying to.")
    parser.add_argument('--rtl', dest='direction', action='store_const',
                        const='rtl', default='ltr',
                        help=("Format the gist as right-to-left text."))
    args = parser.parse_args()
    instance = args.instance
    if instance:
        client_cred_filename = '{}.{}.client.secret'.format(args.app_name, args.instance)
    else:
        candidates = glob('{}.*.client.secret'.format(args.app_name))
        assert candidates, "No app/user registered. Please run register.sh first."
        client_cred_filename = candidates[0]
        instance = client_cred_filename[len(args.app_name)+1:-len('.client.secret')]
    email = args.email
    if email:
        user_cred_filename = '{}.{}.{}.user.secret'.format(
            args.app_name, instance, email.replace('@','.'))
    else:
        candidates = glob('{}.{}.*.user.secret'.format(
            args.app_name, instance))
        assert len(candidates), \
            "No user registered for {} at {}. Please run register.sh first.".format(
                args.app_name, instance)
        user_cred_filename = candidates[0]
    assert \
        os.path.exists(client_cred_filename) and \
            os.path.exists(user_cred_filename), \
        "App/user not registered. Please run register.sh"
    logging.info("Connecting to {}...".format(instance))
    masto = Mastodon(
        client_id = client_cred_filename,
        access_token = user_cred_filename,
        api_base_url = 'https://'+instance)

    if args.web:
        account = masto.account_verify_credentials()
        webserver(masto, instance, account)
    else:
        logging.info("Reading markdown from standard input...")
        lines = [unicode(l,'utf-8') for l in sys.stdin.readlines()]
        assert len(filter(lambda l: l.strip(), lines)), \
            "Empty toot."
        body = u'\n'.join(lines)
        assert not args.title or len(args.title)<=80, "Title exceeds 80 characters"
        if args.re:
            irt = url2toot(masto, args.re)
            assert irt, "not a toot's url: {}".format(args.re)
        else:
            irt = None
        title = args.title
        try:
            title = unicode(title,'utf-8')
        except TypeError:
            pass # Either Null, or already unicode(?!?)
        logging.info("Posted {}.".format(post(
            masto, body, instance,
            title=title, direction=args.direction, in_reply_to=irt)))


if __name__=='__main__':
    main()
