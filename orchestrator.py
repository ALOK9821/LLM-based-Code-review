from requests.exceptions import HTTPError
from pr_fetcher import get_pr_content
from prompt import promptV1
from llm_call import get_pr_chat_completion
import json


def orchestrate(repo_url, pr_number, github_token=None):
    try:
        pr_content = get_pr_content(repo_url, pr_number, github_token)
        per_file_results = []
        for per_file_content in pr_content:
            filename = per_file_content.pop("filename", None)
            prompt = promptV1(per_file_content)
            code_review = json.loads(get_pr_chat_completion(prompt=prompt, model='llama3-8b-8192'))
            per_file_results.append(
                {
                    "name": filename,
                    "issues": code_review['issues']
                }
            )
        return {"files": per_file_results}
    except:
        return {"files": []}


# print(orchestrate('https://github.com/pandas-dev/pandas', '60266'))
    