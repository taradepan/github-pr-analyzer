import base64
import uuid
from groq import Groq
import os, sys
from .github import fetch_pr_files ,fetch_file_content
from .prompts import system_prompt
import json
import dotenv
dotenv.load_dotenv()

def analyze_code_with_llm(file_content, file_name):
    if not file_name or not file_content:
        return {
            "issues": [{
                "type": "error",
                "line": 0,
                "description": "Invalid input - file name or content is missing",
                "suggestion": "Ensure both file name and content are provided"
            }]
        }

    prompt = f"""
    File: {file_name}
    Content:
    {file_content}

    Provide a detailed JSON output with the structure:
    {{
        "issues": [
            {{
                "type": "<style|bug|performance|best_practice>",
                "line": <line_number>,
                "description": "<description>",
                "suggestion": "<suggestion>"
            }}
        ]
    }}
    """
    try:

        client = Groq(
            api_key=os.environ.get("GROQ_API_KEY"),
        )
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {'role': 'system', 'content': system_prompt},
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=1,
            top_p=1,
            response_format={
                "type": "json_object"
            },


        )
    
        return completion.choices[0].message.content
    except Exception as e:
        return {
            "issues": [{
                "type": "error",
                "line": 0,
                "description": f"Analysis failed: {str(e)}",
                "suggestion": "Check input format and try again"
            }]
        }

def analyze_pr(repo_url, pr_number, github_token=None):
    task_id = str(uuid.uuid4())
    try:
        pr_files = fetch_pr_files(repo_url, pr_number, github_token)

        results = {"files": [], "summary": {
            "total_files": 0, "total_issues": 0, "critical_issues": 0}}

        for file in pr_files:
            file_name = file["filename"]
            raw_content = fetch_file_content(repo_url, file_name, github_token)

            analysis_result = analyze_code_with_llm(raw_content, file_name)

            try:
                analysis_data = json.loads(analysis_result)  
            except json.JSONDecodeError as e:
                return {"task_id": task_id, "status": "error", "message": f"JSON decode error: {str(e)}"}


            total_issues = len(analysis_data["issues"])
            critical_issues =  sum(
                    1 for issue in analysis_data["issues"] if issue["type"] == "bug"
                )

            results["files"].append({"name": file_name, "issues": analysis_data["issues"]})

            results["summary"]["total_files"] += 1
            results["summary"]["total_issues"] += total_issues
            results["summary"]["critical_issues"] += critical_issues

        return {"task_id": task_id, "status": "completed", "results": results}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        return {"task_id": task_id, "status": "error", "message": f"{exc_type, fname, exc_tb.tb_lineno,e}"}