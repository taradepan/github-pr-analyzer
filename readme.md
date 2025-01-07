get your Groq API Key from the Groq platform and paste it in the `.env` file (refer .env.example)

run these commands parallely 
`cd fastapi_app & uvicorn main:app --reload`
`cd django_app & celery -A django_app worker -l info -P eventlet`
`cd django_app & python manage.py runserver 0.0.0.0:8001`
