import requests

def fetch_pr_diff(repo_url, pr_number, github_token=None):
    try:
        owner, repo = repo_url.rstrip("/").split("/")[-2:]
    except ValueError:
        raise ValueError("Invalid repository URL format. Should be in the form 'https://github.com/owner/repo'.")

    base_url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {}

    if github_token:
        headers["Authorization"] = f"token {github_token}"

    files_url = f"{base_url}/pulls/{pr_number}/files"
    response = requests.get(files_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch PR files: {response.json().get('message', 'Unknown error')}")

    files_data = response.json()
    pr_changes = {}

    for file_info in files_data:
        file_path = file_info["filename"]
        patch = file_info.get("patch", "")

        new_lines = []
        for line in patch.splitlines():
            if line.startswith("+") and not line.startswith("+++"):
                new_lines.append(line[1:])  

        pr_changes[file_path] = "\n".join(new_lines)

    return pr_changes
