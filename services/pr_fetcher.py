import logging
import requests
import re
from services.prompt import promptV1

# Configure structured logging
logging.basicConfig(level=logging.INFO, format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}')
logger = logging.getLogger(__name__)

def fetch_pr_files(repo_owner, repo_name, pr_number, github_token=None):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/files"
    headers = {'Authorization': f'token {github_token}'} if github_token else {}
    
    try:
        logger.info("Fetching PR files", extra={"repo_owner": repo_owner, "repo_name": repo_name, "pr_number": pr_number})
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error("Error fetching PR files", exc_info=True, extra={"repo_owner": repo_owner, "repo_name": repo_name, "pr_number": pr_number})
        raise ConnectionError(f"Error fetching pull request files: {e}")

def extract_added_lines(pr_files):
    file_contents = []
    for file in pr_files:
        file_name = file['filename']
        patch = file.get("patch")
        added_lines = {"filename": file_name}
        
        if not patch:
            continue 
        
        line_number = None
        for line in patch.split('\n'):
            match = re.match(r'^@@ -\d+,\d+ \+(\d+),\d+ @@', line)
            if match:
                line_number = int(match.group(1))
                continue
            if line.startswith('+') and not line.startswith('+++'):
                code_line = line[1:].strip()
                added_lines[line_number] = code_line
                line_number += 1
            elif not line.startswith('-'):
                line_number += 1
        file_contents.append(added_lines)
                
    logger.info("Extracted added lines", extra={"file_count": len(file_contents)})
    return file_contents


def get_pr_content(repo_url, pr_number, github_token=None):
    try:
        repo_owner, repo_name = repo_url.rstrip("/").split("/")[-2:]
    except ValueError:
        raise ValueError("Invalid repository URL format. Should be in the form 'https://github.com/owner/repo'.")
    
    try:
        pr_files = fetch_pr_files(repo_owner, repo_name, pr_number, github_token)
        added_lines = extract_added_lines(pr_files)
        logger.info("Fetched and processed PR content", extra={"repo_url": repo_url, "pr_number": pr_number})
        return added_lines
    except (ConnectionError, RuntimeError) as e:
        logger.error("Error in get_pr_content", exc_info=True, extra={"repo_url": repo_url, "pr_number": pr_number})
        return None
