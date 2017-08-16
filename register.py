import os
import argparse
from getpass import getpass
from mastodon import Mastodon

def create_app(instance, app_name, to_file):
    Mastodon.create_app(
        app_name,
        api_base_url = 'https://'+instance,
        to_file = to_file)
    os.chmod(to_file, 0600)

def sign_up(instance, client_cred, email, password, to_file):
    masto = Mastodon(
        client_id = client_cred,
        api_base_url = 'https://'+instance)
    masto.log_in(email, password, scopes = ['read', 'write'],
        to_file = to_file)
    os.chmod(to_file, 0600)
    return masto

def sign_in(instance, client_cred, user_cred):
    masto = Mastodon(
        client_id = client_cred,
        access_token = user_cred,
        api_base_url = 'https://'+instance)
    return masto

if __name__=='__main__':
    when = "already"
    parser = argparse.ArgumentParser(description='Authorize Gistodon app for a mastodon account.')
    parser.add_argument('-a', '--app_name', default='Gistodon',
                        help=('Name for the app (default is Gistodon).'
                              ' Appears below the toot, near the date.'))
    parser.add_argument('instance', help='Your mastodon instance (e.g. mastodon.social).')
    parser.add_argument('email',
                        help='The email address you login to that instance with.')
    args = parser.parse_args()
    client_cred_filename = '{}.{}.client.secret'.format(args.app_name, args.instance)
    user_cred_filename = '{}.{}.{}.user.secret'.format(
        args.app_name, args.instance, args.email.replace('@','.'))
    if not os.path.exists(client_cred_filename):
        print "Creating the {} app at {}...".format(
            args.app_name, args.instance)
        create_app(args.instance, args.app_name, client_cred_filename)
        print "created {}.".format(client_cred_filename)
        when = "now"
    masto = None
    if os.path.exists(user_cred_filename):
        masto = sign_in(
            args.instance, client_cred_filename, user_cred_filename)
    else:
        passwd = None
        while not passwd:
            passwd = getpass("Enter {}'s password at {}: ".format(
                args.email, args.instance))
        masto = sign_up(
            args.instance, client_cred_filename,
            args.email, passwd, user_cred_filename)
        print "created {}.".format(user_cred_filename)
        when = "now"
    print "You're {} registered as {}".format(
        when, masto.account_verify_credentials()['url'])
