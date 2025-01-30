import requests
import json
from datetime import datetime
import os

# GitHub username
username = "gofullthrottle"

# GitHub token
token = os.getenv("GITHUB_TOKEN")

def get_repos(url):
    repos = []
    while url:
        response = requests.get(url, auth=(username, token))
        if response.status_code != 200:
            raise Exception(f"Failed to fetch data: {response.status_code}")
        repos.extend(response.json())
        url = response.links.get('next', {}).get('url')
    return repos

def get_repo_details(repo):
    response = requests.get(f"https://api.github.com/repos/{repo['full_name']}", auth=(username, token))
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data: {response.status_code}")
    details = response.json()
    return details

def main():
    starred_repos_url = f"https://api.github.com/users/{username}/starred"
    forked_repos_url = f"https://api.github.com/users/{username}/repos?type=fork"

    starred_repos = get_repos(starred_repos_url)
    forked_repos = get_repos(forked_repos_url)

    all_repos = starred_repos + forked_repos

    repo_details = []
    for repo in all_repos:
        details = get_repo_details(repo)
        repo_details.append({
            "name": repo["name"],
            "full_name": repo["full_name"],
            "description": repo["description"],
            "stars": details["stargazers_count"],
            "last_commit": details["pushed_at"]
        })

    # Sort repos by last commit date
    repo_details.sort(key=lambda x: datetime.strptime(x['last_commit'], "%Y-%m-%dT%H:%M:%SZ"), reverse=True)

    # Generate markdown document
    with open("repos.md", "w") as file:
        file.write("# Starred and Forked Repositories\n\n")
        file.write("| Repository | Description | Stars | Last Commit |\n")
        file.write("|------------|-------------|-------|-------------|\n")
        for repo in repo_details:
            file.write(f"| [{repo['name']}](https://github.com/{repo['full_name']}) | {repo['description']} | {repo['stars']} | {repo['last_commit']} |\n")

if __name__ == "__main__":
    main()
