import logging
from celery import Celery
from services.orchestrator import orchestrate
import os

logging.basicConfig(level=logging.INFO, format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}')
logger = logging.getLogger(__name__)

broker_url = os.environ.get('BROKER_URL', 'redis://localhost:6379/0')
backend_url = os.environ.get('BACKEND_URL', 'redis://localhost:6379')
celery_app = Celery("code_review_agent", broker=broker_url, backend=backend_url)

@celery_app.task(bind=True)
def analyze_pr_task(self, repo_url, pr_number, github_token=None):
    try:
        logger.info("Starting orchestration", extra={"repo_url": repo_url, "pr_number": pr_number})
        results = orchestrate(repo_url, pr_number, github_token)
        logger.info("Orchestration completed", extra={"repo_url": repo_url, "pr_number": pr_number})
        return results
    except Exception as e:
        logger.error("Orchestration failed", exc_info=True, extra={"repo_url": repo_url, "pr_number": pr_number})
        self.update_state(state="FAILURE", meta={"exc_type": str(type(e)), "exc_message": str(e)})
        raise e
