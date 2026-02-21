import os
import base64
import requests
from datetime import datetime


def upload_file(repo, token, file_path, repo_path):

    with open(file_path, "rb") as f:
        content = base64.b64encode(f.read()).decode()

    url = f"https://api.github.com/repos/{repo}/contents/{repo_path}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    data = {
        "message": f"Upload {repo_path}",
        "content": content
    }

    response = requests.put(url, json=data, headers=headers)

    if response.status_code not in [200, 201]:
        raise Exception(response.text)


def upload_folder_to_github(folder_path, repo, token):

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for root, dirs, files in os.walk(folder_path):
        for file in files:

            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, folder_path)

            # 👇 This creates unique folder per validation
            repo_path = f"validation_results/validation_{timestamp}/{relative_path}"

            upload_file(repo, token, full_path, repo_path)