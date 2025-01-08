### 1) Clone the repo
### 2) get your Groq API Key from the Groq platform and paste it in the `.env` file (refer .env.example)

### 3) run these commands parallely 

`cd fastapi_app & uvicorn main:app --reload`

`cd django_app & celery -A django_app worker -l info -P eventlet`

`cd django_app & python manage.py runserver 0.0.0.0:8001`




### 4) Test it with Postman or Curl

`curl -X POST \
  'http://127.0.0.1:8001/start_task/' \
  -H 'Content-Type: application/json' \
  -d '{
    "repo_url": "https://github.com/<username>/<reponame>",
    "pr_number": <pr-number>,
    "github_token": null
  }'
  `

`curl  http:///127.0.0.1:8001/task_status/<task_id>/`

`curl  http:///127.0.0.1:8001/task_result/<task_id>/`


### Implementation:
- FastAPI is used for frontend service due to its high performance and async capabilities.
- Django is used for backend where majority of the logic is implemented.
- Using `api.github.com` to fetch the pr data.
- Celery for task queue to handle long-running analysis jobs.
- Redis as message broker for its speed and reliability.
- Using Groq as LLM provider as it is free to use and has LLAMA3.3 70b.


### Future Improvements:
- Use chunking for pull requests with token length exceding the context length of the model
- Integrate with github apps to automate the review process


