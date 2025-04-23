import json
import os
import requests

GITHUB_API_URL = "https://api.github.com/repos/"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

with open("highlighted_repos.json", "r") as f:
    highlighted_repos = json.load(f)

cached_data = []

for entry in highlighted_repos:
    match = entry["repo_url"].split("github.com/")[-1].split("/")
    if len(match) < 2:
        continue
    owner, repo = match[0], match[1]

    response = requests.get(f"{GITHUB_API_URL}{owner}/{repo}", headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to fetch {owner}/{repo}: {response.status_code}")
        continue

    data = response.json()

    cached_data.append(
        {
            "name": data.get("name"),
            "full_name": data.get("full_name"),
            "html_url": data.get("html_url"),
            "language": data.get("language"),
            "description": entry.get("blurb") or data.get("description"),
            "stargazers_count": data.get("stargazers_count"),
            "forks_count": data.get("forks_count"),
            "updated_at": data.get("updated_at"),
            "keyword": entry.get("keyword"),
            "demo": entry.get("demo"),
        }
    )

with open("projects-cache.json", "w") as f:
    json.dump(cached_data, f, indent=2)
