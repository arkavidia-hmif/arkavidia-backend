#!/bin/sh

/code/manage.py migrate
cd /code
gunicorn arkav.wsgi