#!/bin/sh
cd "$(dirname "$0")"
. venv/bin/activate
python register.py "$@"
