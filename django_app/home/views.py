from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from .task import analyze_repo_task
from .models import *
from celery.result import AsyncResult
import json
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
def start_task(request):
    if request.method != "POST":
        return JsonResponse({"message": "Only POST method is allowed"}, status=405)
    
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            repo_url = data.get('repo_url')
            pr_number = data.get('pr_number')
            github_token = data.get('github_token')
        else:
            repo_url = request.POST.get('repo_url')
            pr_number = request.POST.get('pr_number')
            github_token = request.POST.get('github_token')

        logger.debug(f"Received request - URL: {repo_url}, PR: {pr_number}")

        if not repo_url or not pr_number:
            return JsonResponse({
                "error": "Missing required fields: repo_url and pr_number"
            }, status=400)
        
        task = analyze_repo_task.delay(repo_url, pr_number, github_token)
        return JsonResponse({"task_id": task.id, "status": "Task started"})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
def task_status_view(request, task_id):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        result = AsyncResult(task_id)
        return JsonResponse({
            'task_id': task_id,
            'status': result.state.lower()
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

@csrf_exempt
def task_result_view(request, task_id):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        result = AsyncResult(task_id)
        if result.state == 'SUCCESS':
            task_result = result.get()
            if isinstance(task_result, dict) and 'results' in task_result:
                return JsonResponse({
                    'task_id': task_id,
                    'status': 'completed',
                    'files': task_result['results']['files'],
                    'summary': task_result['results']['summary']
                })
            return JsonResponse({
                'task_id': task_id,
                'status': 'completed',
                'result': task_result
            })
        elif result.state == 'FAILURE':
            return JsonResponse({
                'task_id': task_id,
                'status': 'failed',
                'error': str(result.result)
            })
        else:
            return JsonResponse({
                'task_id': task_id,
                'status': result.state.lower(),
                'message': 'Result not ready'
            })
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)