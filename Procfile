release: ./release.sh
web: gunicorn config.wsgi
worker: celery worker --app config.celery.app