import os
import base64
import requests
from datetime import datetime
import requests


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
        raise Exception(f"GitHub Upload Failed: {response.text}")

    return repo_path


def upload_folder_to_github(folder_path, repo, token):

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    uploaded_files = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:

            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, folder_path)

            repo_path = f"validation_results/validation_{timestamp}/{relative_path}"

            upload_file(repo, token, full_path, repo_path)

            uploaded_files.append(repo_path)

    return uploaded_files, timestamp




def get_folder_contents(repo, token, path):

    url = f"https://api.github.com/repos/{repo}/contents/{path}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 404:
        return []

    if response.status_code != 200:
        raise Exception(response.text)

    return response.json()


def delete_file(repo, token, path, sha):

    url = f"https://api.github.com/repos/{repo}/contents/{path}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    data = {
        "message": f"Delete {path}",
        "sha": sha
    }

    response = requests.delete(url, json=data, headers=headers)

    if response.status_code not in [200]:
        raise Exception(response.text)


def delete_folder_recursive(repo, token, folder_path):

    contents = get_folder_contents(repo, token, folder_path)

    for item in contents:

        if item["type"] == "file":
            delete_file(repo, token, item["path"], item["sha"])

        elif item["type"] == "dir":
            delete_folder_recursive(repo, token, item["path"])