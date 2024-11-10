import requests
import re
from prompt import promptV1

def fetch_pr_files(repo_owner, repo_name, pr_number, github_token=None):
    """Fetch the list of files in a GitHub pull request."""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/files"
    headers = {'Authorization': f'token {github_token}'} if github_token else {}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise ConnectionError(f"Error fetching pull request files: {e}")

def extract_added_lines(pr_files):
    """Extract added lines from the diff in the pull request files."""
    file_contents = []
    
    
    for file in pr_files:
        file_name = file['filename']
        patch = file.get("patch")
        added_lines = {"filename": file_name}
        if not patch:
            continue  # Skip files without a patch (e.g., binary files)
        
        line_number = None  
        
        for line in patch.split('\n'):
            match = re.match(r'^@@ -\d+,\d+ \+(\d+),\d+ @@', line)
            if match:
                line_number = int(match.group(1))
                continue
            # Process added lines (lines starting with '+')
            if line.startswith('+') and not line.startswith('+++'):
                code_line = line[1:].strip()  
                added_lines[line_number] = code_line
                line_number += 1
            elif not line.startswith('-'):  # Skip deleted lines
                line_number += 1 
        file_contents.append(added_lines)
                
    return file_contents


def get_pr_content(repo_url, pr_number, github_token=None):
    """
    Main function to fetch pull request files, extract added lines,
    
    Parameters:
        - repo_url: Repository url (string)
        - pr_number: Pull request number (int)
        - github_token: GitHub API token (optional, string)
    
    Returns:
        - line wise file content from pr (object)
    
    Raises:
        - ConnectionError for network/API issues.
    """
    try:
        repo_owner, repo_name = repo_url.rstrip("/").split("/")[-2:]
    except ValueError:
        raise ValueError("Invalid repository URL format. Should be in the form 'https://github.com/owner/repo'.")
    
    try:
        pr_files = fetch_pr_files(repo_owner, repo_name, pr_number, github_token)
        added_lines = extract_added_lines(pr_files)
        return added_lines
    except (ConnectionError, RuntimeError) as e:
        print(f"An error occurred: {e}")
        return None
    