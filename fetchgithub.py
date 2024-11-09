import requests

def fetch_pr_files(repo_url, pr_number, github_token=None):
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
    file_contents = {}

    for file_info in files_data:
        file_path = file_info["filename"]
        blob_url = file_info["contents_url"] 

        file_response = requests.get(blob_url, headers=headers)
        if file_response.status_code == 200:
            file_data = file_response.json()
            file_contents[file_path] = file_data["content"] 
        else:
            raise Exception(f"Failed to fetch content for {file_path}: {file_response.json().get('message', 'Unknown error')}")

    return file_contents
