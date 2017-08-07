import os, sys, re, argparse, time, json
import requests
from glob import glob
from getpass import getpass
from mastodon import Mastodon
from markdown import markdown
from html_text import extract_text
from flask import Flask, render_template, request, redirect

DEBUG = False

RE_MENTION = re.compile(r'@(\w+)@([\w.]+)')

def get_mentions(s, ignore=None):
    mentions = set([
        "@{}@{}".format(user,instance)
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

def post(masto, body, title=None):
    summary = extract_text(markdown(body.strip()[:140]))
    gist = make_gist(
        title or u"A gistodon toot, {} GMT".format(
            time.asctime(time.gmtime())),
        linkify_mentions(body)+u"""

###### Generated by [Gistodon](https://github.com/thedod/gistodon/#readme).""")
    status = u'{}... {}'.format(summary, gist)
    mentions = get_mentions(body, ignore=summary)
    if mentions:
        status += u'\n'+u' '.join(mentions)
    return masto.status_post(status, spoiler_text=title)['url']

def webserver(masto, account):
    app = Flask(__name__, static_url_path='')
 
    @app.route('/')
    def index():
        return render_template('index.html', account=account)

    @app.route('/toot', methods=['POST'])
    def tootit():
        if not request.form['markdown'].strip():
            return "Nothing to toot"
        return redirect(post(
            masto, request.form['markdown'], request.form['title']))

    app.run(host='localhost', port=8008, debug=DEBUG)

def main():
    parser = argparse.ArgumentParser(
        description="Toot stdin as a gist [markdown is supported].")
    parser.add_argument('--web', '-w', action="store_true",
                        help="Run as a web server on localhost.")
    parser.add_argument('--title', '-t',
                        help="Optional: gist's title, and the toot's content warning (CW).")
    parser.add_argument('--instance', '-i',
                        help='Your mastodon instance (e.g. mastodon.social).')
    parser.add_argument('--email', '-e',
                        help='The email address you login to that instance with.')
    parser.add_argument('--app_name', '-a', default='Gistodon',
                        help='Name for the app (default is Gistodon).')
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
    masto = Mastodon(
        client_id = client_cred_filename,
        access_token = user_cred_filename,
        api_base_url = 'https://'+instance)

    if args.web:
        account = masto.account_verify_credentials()
        webserver(masto, account)
    else:
        lines = sys.stdin.readlines()
        assert len(filter(lambda l: l.strip(), lines)), \
            "Empty toot."
        body = '\n'.join(lines)
        assert not args.title or len(args.title)<=80, "Title exceeds 80 characters"
        print post(masto, body, title)


if __name__=='__main__':
    main()
