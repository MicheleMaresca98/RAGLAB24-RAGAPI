#!/bin/sh
set -ue

case "${1:-}" in
  -shell)
    exec python
    ;;

  -sh)
    exec /bin/sh
    ;;

  -worker)
    exec python -m celery -A django_core.celery worker -l INFO -E --without-gossip --without-mingle --without-heartbeat --autoscale=8,2
    ;;

  -worker-debug)
    exec python -m debugpy --listen 0.0.0.0:5680 -m celery -A django_core.celery worker -l DEBUG -E --without-gossip --without-mingle --without-heartbeat --autoscale=8,2
    ;;

  -start)
    exec uwsgi --module django_core.wsgi:application --master --workers 8 --socket :8000
    ;;

  -start-debug)
    exec python /src/manage.py runserver 0.0.0.0:8000
    ;;

esac
