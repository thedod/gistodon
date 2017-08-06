#!/bin/sh
cd "$(dirname "$0")"
virtualenv -p python2 venv
. venv/bin/activate
pip install -r requirements.txt
echo now run register.sh [-h]
