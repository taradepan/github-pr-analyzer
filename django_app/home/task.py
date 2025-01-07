from celery import Celery
from django.core.files.base import ContentFile
from django.utils import timezone
from .models import TaskStatus
import base64
import time
import requests
from groq import Groq
from celery import shared_task
from .models import RepoData


app = Celery('django_app')
app.config_from_object('django.conf:settings', namespace='CELERY')
from home.utils.ai_agent import analyze_pr
 

@shared_task
def analyze_repo_task(owner, repo, github_token=None):
    result = analyze_pr(owner, repo, github_token=None)
    return result