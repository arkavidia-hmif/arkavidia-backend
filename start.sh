#!/bin/sh

/code/manage.py migrate
/code/manage.py collectstatic --noinput
/code/manage.py crontab add
/code/manage.py rqworker &
gunicorn --pythonpath backend arkav.wsgi --bind 0.0.0.0:8000