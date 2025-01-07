get your Groq API Key from the Groq platform and paste it in the `.env` file (refer .env.example)

run these commands parallely 

`cd fastapi_app & uvicorn main:app --reload`

`cd django_app & celery -A django_app worker -l info -P eventlet`

`cd django_app & python manage.py runserver 0.0.0.0:8001`



Test it with Postman or Curl

`curl -X POST \
  'http://127.0.0.1:8001/start_task/' \
  -H 'Content-Type: application/json' \
  -d '{
    "repo_url": "https://github.com/<username>/<reponame>",
    "pr_number": 82,
    "github_token": null
  }'
  `

`curl  http:///127.0.0.1:8001/task_status/<task_id>/`

`curl  http:///127.0.0.1:8001/task_result/<task_id>/`
