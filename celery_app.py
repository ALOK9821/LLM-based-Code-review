from celery import Celery
import base64
from requests.exceptions import HTTPError
from orchestrator import orchestrate
celery_app = Celery("code_review_agent", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0")

@celery_app.task(bind=True)
def analyze_pr_task(self, repo_url, pr_number, github_token=None):
    try:
        results = orchestrate(repo_url, pr_number, github_token)
        return results

    except Exception as e:
        self.update_state(state="FAILURE", meta={"exc_type": str(type(e)), "exc_message": str(e)})
        raise e

