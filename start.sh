#!/bin/sh

/code/manage.py migrate
/code/manage.py collectstatic
gunicorn --pythonpath backend arkav.wsgi --bind 0.0.0.0:8000