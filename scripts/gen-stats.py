#!/usr/bin/env python3
"""Generate assets/stats.svg and assets/top-langs.svg for the profile README.

Reads the GitHub GraphQL API with GH_TOKEN (or GITHUB_TOKEN). Standard library only.
"""
import json
import os
import sys
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
from theme import ICON, MUTED, PALETTE, TEXT, titled_card as card  # noqa: E402

LOGIN = os.environ.get("STATS_LOGIN", "simnJS")
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
OUT = Path(__file__).resolve().parent.parent / "assets"

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
    }
    pullRequests(first: 1) { totalCount }
    issues(first: 1) { totalCount }
    repositoriesContributedTo(first: 1, contributionTypes: [COMMIT, PULL_REQUEST, ISSUE, REPOSITORY]) { totalCount }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
  }
}
"""


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        body = json.load(res)
    if "errors" in body:
        raise SystemExit(f"GraphQL error: {body['errors']}")
    return body["data"]["user"]


def stats_card(user):
    stars = sum(r["stargazerCount"] for r in user["repositories"]["nodes"])
    cc = user["contributionsCollection"]
    rows = [
        ("Total stars", stars, "M8 .25a.75.75 0 0 1 .67.42l1.88 3.8 4.2.61a.75.75 0 0 1 .42 1.28l-3.04 2.96.72 4.18a.75.75 0 0 1-1.09.79L8 12.3l-3.76 1.98a.75.75 0 0 1-1.09-.79l.72-4.18L.83 6.36a.75.75 0 0 1 .42-1.28l4.2-.61L7.33.67A.75.75 0 0 1 8 .25Z"),
        ("Commits (last year)", cc["totalCommitContributions"] + cc["restrictedContributionsCount"], "M11.93 8.5a4 4 0 0 1-7.86 0H.75a.75.75 0 0 1 0-1.5h3.32a4 4 0 0 1 7.86 0h3.32a.75.75 0 0 1 0 1.5Zm-1.43-.75a2.5 2.5 0 1 0-5 0 2.5 2.5 0 0 0 5 0Z"),
        ("Pull requests", user["pullRequests"]["totalCount"], "M1.5 3.25a2.25 2.25 0 1 1 3 2.12v5.26a2.25 2.25 0 1 1-1.5 0V5.37a2.25 2.25 0 0 1-1.5-2.12Zm9.5-.5h1.25a1 1 0 0 1 1 1v6.88a2.25 2.25 0 1 1-1.5 0V3.75a.25.25 0 0 0-.25-.25H11Z"),
        ("Issues", user["issues"]["totalCount"], "M8 9.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3ZM8 0a8 8 0 1 1 0 16A8 8 0 0 1 8 0ZM1.5 8a6.5 6.5 0 1 0 13 0 6.5 6.5 0 0 0-13 0Z"),
        ("Contributed to", user["repositoriesContributedTo"]["totalCount"], "M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.71 1.71.75.75 0 0 1-1.06 1.06A2.5 2.5 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.71c.3-.14.64-.21 1-.21h8Z"),
    ]
    body = []
    for i, (label, value, path) in enumerate(rows):
        y = 62 + i * 21
        body.append(
            f'<g transform="translate(25,{y - 12})"><path d="{path}" fill="{ICON}" transform="scale(0.8)"/></g>'
            f'<text x="50" y="{y}" font-size="13" fill="{TEXT}">{escape(label)}:</text>'
            f'<text x="285" y="{y}" font-size="13" font-weight="700" fill="{TEXT}" text-anchor="end">{value:,}</text>'
        )
    return card(320, 165, f"{LOGIN}'s GitHub stats", "".join(body))


def langs_card(user):
    totals = {}
    for repo in user["repositories"]["nodes"]:
        for edge in repo["languages"]["edges"]:
            totals[edge["node"]["name"]] = totals.get(edge["node"]["name"], 0) + edge["size"]
    top = sorted(totals.items(), key=lambda kv: -kv[1])[:8]
    total = sum(size for _, size in top) or 1

    width, bar_x, bar_w = 300, 25, 250
    body, x = [], bar_x
    body.append(f'<clipPath id="bar"><rect x="{bar_x}" y="52" width="{bar_w}" height="8" rx="4"/></clipPath><g clip-path="url(#bar)">')
    for i, (_, size) in enumerate(top):
        w = bar_w * size / total
        body.append(f'<rect x="{x:.2f}" y="52" width="{w:.2f}" height="8" fill="{PALETTE[i]}"/>')
        x += w
    body.append("</g>")
    for i, (name, size) in enumerate(top):
        col, row = i % 2, i // 2
        cx, cy = 25 + col * 130, 84 + row * 20
        body.append(
            f'<circle cx="{cx + 5}" cy="{cy - 4}" r="5" fill="{PALETTE[i]}"/>'
            f'<text x="{cx + 16}" y="{cy}" font-size="11" fill="{TEXT}">{escape(name)} '
            f'<tspan fill="{MUTED}">{100 * size / total:.1f}%</tspan></text>'
        )
    return card(width, 165, "Top languages", "".join(body))


def main():
    if not TOKEN:
        raise SystemExit("Set GH_TOKEN or GITHUB_TOKEN")
    user = fetch()
    OUT.mkdir(exist_ok=True)
    (OUT / "stats.svg").write_text(stats_card(user), encoding="utf-8")
    (OUT / "top-langs.svg").write_text(langs_card(user), encoding="utf-8")
    print("wrote assets/stats.svg and assets/top-langs.svg")


if __name__ == "__main__":
    main()
