from celery import Celery
import base64
from requests.exceptions import HTTPError
from fetchgithub import fetch_pr_diff
from llm_review import llm_code_review

celery_app = Celery("code_review_agent", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0")

@celery_app.task(bind=True)
def analyze_pr_task(self, repo_url, pr_number, github_token=None):
    try:
        files = fetch_pr_diff(repo_url, pr_number, github_token)
        
        decoded_files = {}
        for file_name, encoded_content in files.items():
            # decoded_content = base64.b64decode(encoded_content).decode("utf-8")
            decoded_files[file_name] = encoded_content

        analysis_results = {"files": []}
        for file_name, code in decoded_files.items():
            file_review = {
                "file_name": file_name,
                "style_issues": llm_code_review(code, prompt_type="style"),
                "bug_issues": llm_code_review(code, prompt_type="bug"),
                "performance_issues": llm_code_review(code, prompt_type="performance"),
                "best_practices": llm_code_review(code, prompt_type="best_practices")
            }
            analysis_results["files"].append(file_review)

        return {"status": "completed", "results": analysis_results}

    except Exception as e:
        self.update_state(state="FAILURE", meta={"exc_type": str(type(e)), "exc_message": str(e)})
        raise e


def llm_review_placeholder(files):
    issues = []
    for file_name, content in files.items():
        issues.append({
            "file": file_name,
            "issues": [
                {
                    "type": "style",
                    "line": 10,
                    "description": "Line too long",
                    "suggestion": "Break line into multiple lines"
                },
                {
                    "type": "bug",
                    "line": 22,
                    "description": "Potential null pointer",
                    "suggestion": "Add a null check"
                }
            ]
        })
    
    return {
        "files": issues,
        "summary": {
            "total_files": len(files),
            "total_issues": len(issues),
            "critical_issues": len([issue for issue in issues if issue["issues"]])
        }
    }
