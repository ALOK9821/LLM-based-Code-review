import logging
import json
from services.pr_fetcher import get_pr_content
from services.llm_call import get_pr_chat_completion
from services.prompt import promptV1


logging.basicConfig(level=logging.INFO, format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}')
logger = logging.getLogger(__name__)

def orchestrate(repo_url, pr_number, github_token=None):
    try:
        logger.info("Fetching PR content", extra={"repo_url": repo_url, "pr_number": pr_number})
        pr_content = get_pr_content(repo_url, pr_number, github_token)
        
        per_file_results = []
        for per_file_content in pr_content:
            filename = per_file_content.pop("filename", None)
            logger.info("Generating prompt for file", extra={"filename": filename})
            prompt = promptV1(per_file_content)
            
            code_review = json.loads(get_pr_chat_completion(prompt=prompt))
            per_file_results.append(
                {
                    "name": filename,
                    "issues": code_review['issues']
                }
            )
        logger.info("Orchestration completed", extra={"repo_url": repo_url, "pr_number": pr_number})
        return {"files": per_file_results}
    except Exception as e:
        logger.error("Error in orchestration", exc_info=True, extra={"repo_url": repo_url, "pr_number": pr_number})
        return {"files": []}
