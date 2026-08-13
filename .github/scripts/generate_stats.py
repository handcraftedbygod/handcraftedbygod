import json
import os
import urllib.request

USERNAME = "handcraftedbygod"
TOKEN = os.environ["GH_TOKEN"]
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "User-Agent": USERNAME,
    "Accept": "application/vnd.github+json",
}
COLORS = ["#f2f2f2", "#aaaaaa", "#777777", "#4a4a4a", "#2a2a2a"]
LABEL_X = [20, 130, 210, 290, 360]


def api(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def graphql(query):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers=HEADERS,
    )
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def owned_repos():
    repos, page = [], 1
    while True:
        batch = api(f"https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}")
        if not batch:
            return repos
        repos.extend(r for r in batch if not r["fork"])
        page += 1


def render_svg(public_repos, stars, contributions, top_langs, total_bytes):
    bars, labels = [], []
    x = 20
    for i, (lang, count) in enumerate(top_langs):
        pct = count / total_bytes * 100
        width = round(pct / 100 * 380)
        bars.append(f'  <rect x="{x}" y="108" width="{width}" height="10" fill="{COLORS[i]}"/>')
        labels.append(
            f'  <text x="{LABEL_X[i]}" y="134" fill="#666" font-size="10">{lang} {round(pct)}%</text>'
        )
        x += width

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="420" height="150" viewBox="0 0 420 150" font-family="ui-monospace, monospace">
  <rect width="420" height="150" rx="10" fill="#000"/>
  <rect x="0.5" y="0.5" width="419" height="149" rx="10" fill="none" stroke="#333"/>

  <text x="20" y="30" fill="#888" font-size="12">public repos</text>
  <text x="400" y="30" fill="#eee" font-size="12" text-anchor="end">{public_repos}</text>

  <text x="20" y="52" fill="#888" font-size="12">stars</text>
  <text x="400" y="52" fill="#eee" font-size="12" text-anchor="end">{stars}</text>

  <text x="20" y="74" fill="#888" font-size="12">contributions, past year</text>
  <text x="400" y="74" fill="#eee" font-size="12" text-anchor="end">{contributions}</text>

  <text x="20" y="100" fill="#888" font-size="11">languages</text>

{chr(10).join(bars)}

{chr(10).join(labels)}
</svg>
"""


def main():
    profile = api(f"https://api.github.com/users/{USERNAME}")
    repos = owned_repos()
    stars = sum(r["stargazers_count"] for r in repos)

    contrib = graphql(
        f'query {{ user(login: "{USERNAME}") '
        "{ contributionsCollection { contributionCalendar { totalContributions } } } }"
    )
    contributions = contrib["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]

    lang_bytes = {}
    for r in repos:
        for lang, count in api(r["languages_url"]).items():
            lang_bytes[lang] = lang_bytes.get(lang, 0) + count
    total_bytes = sum(lang_bytes.values()) or 1
    top_langs = sorted(lang_bytes.items(), key=lambda kv: kv[1], reverse=True)[:5]

    svg = render_svg(profile["public_repos"], stars, contributions, top_langs, total_bytes)
    with open("stats.svg", "w", newline="\n") as f:
        f.write(svg)


if __name__ == "__main__":
    main()
