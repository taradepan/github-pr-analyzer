web: gunicorn django_app.wsgi:application --log-file -
fastapi: uvicorn fastapi_app.main:app --host=0.0.0.0 --port=${PORT}
worker: celery -A django_app worker --loglevel=info