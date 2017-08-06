import os
import sys
import re
import argparse
from glob import glob
from getpass import getpass
import requests
from mastodon import Mastodon

RE_MENTION = re.compile(r'@(\w+)@([\w.]+)')

def get_mentions(s):
    return set([
        "@{}@{}".format(user,instance)
        for user, instance in RE_MENTION.findall(s)])

def linkify_mentions(s):
    return RE_MENTION.sub(
        lambda m:
            "[@{user}](https://{instance}/@{user})".format(
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
                    "content": "### {}\n\n{}".format(title, body)
                }
            }
        }
    ).json()['html_url']+"#file-toot-md"

if __name__=='__main__':
    parser = argparse.ArgumentParser(
        description="Toot stdin as a gist [markdown is supported].")
    parser.add_argument('--instance', '-i',
                        help='Your mastodon instance (e.g. mastodon.social).')
    parser.add_argument('--email', '-e',
                        help='The email address you login to that instance with.')
    parser.add_argument('--app_name', '-a', default='Gistodon',
                        help='Name for the app (default is Gistodon).')
    args = parser.parse_args()
    lines = sys.stdin.readlines()
    assert len(filter(lambda l: l.strip(), lines))>1, \
        "You need at least 2 non-empty lines. First line is used as a title."
    title, body = lines[0].strip(), '\n'.join(lines[1:])
    assert len(title), "First line (the title) shouldn't be empty"
    assert len(title)<=80, "Title exceeds 80 characters"
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
    status = make_gist(title, linkify_mentions(body))
    mentions = get_mentions(body)
    if mentions:
        status += '\n'+' '.join(mentions)
    print masto.status_post(status, spoiler_text=title)['url']
