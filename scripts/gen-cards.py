#!/usr/bin/env python3
"""Generate the project cards in assets/cards/ for the profile README.

Live numbers (stars, downloads, merged PRs) come from the GitHub REST API with GH_TOKEN
(or GITHUB_TOKEN). When a lookup fails, the card falls back to its static text.
Standard library only.
"""
import json
import os
import sys
import textwrap
import urllib.parse
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
from theme import CHIP, MUTED, PALETTE, TEXT, TITLE, svg  # noqa: E402

LOGIN = os.environ.get("STATS_LOGIN", "simnJS")
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
OUT = Path(__file__).resolve().parent.parent / "assets" / "cards"
WIDTH, HEIGHT = 400, 118

CARDS = [
    dict(slug="stake-dev-tool", name="Stake Dev Tool", where="Stake-Dev-Tool/stake-dev-tool",
         text="Open-source workbench and cloud platform for Stake Engine slot games.",
         tags=["Rust", "Svelte"], repo="Stake-Dev-Tool/stake-dev-tool", stat="downloads", fallback="↓ 7k"),
    dict(slug="anyps5", name="AnyPS5", where="boykopovar/AnyPS5 · contributor",
         text="Ports PS5 executables to Linux and Windows. My part: libc, FreeType, JavaScriptCore.",
         tags=["C++"], repo="boykopovar/AnyPS5", stat="stars", prs_repo="boykopovar/AnyPS5"),
    dict(slug="prism-verse", name="prism-verse", where="simnJS/prism-verse",
         text="Typed player data for UEFN Verse: one schema, generated persistence and migrations.",
         tags=["TypeScript", "Verse"], repo="simnJS/prism-verse", stat="stars"),
    dict(slug="verse-tooling", name="Verse tooling", where="verse-native-bench · BetterVerse · highlightjs-verse",
         text="Benchmarks and faster drop-ins for Verse, plus syntax colors on GitHub and highlight.js.",
         tags=["Verse", "Linguist", "highlight.js"]),
    dict(slug="playnchill", name="Play'n Chill", where="playandchill.bet",
         text="Independent slot studio and Stake Engine provider, on our own Pixi.js front-end engine.",
         tags=["Pixi.js", "Stake Engine"]),
    dict(slug="playnchill-roblox", name="Play'n Chill · Roblox", where="Roblox community",
         text="Roblox studio: Planet Tycoon, Weapons RNG, 100 Players Enter Youtubers.",
         tags=["Roblox", "Luau"]),
    dict(slug="store", name="simnJS Store", where="store.simnjs.fr",
         text="Ready-to-use Verse code, game systems and UI for UEFN creators, tested in-game.",
         tags=["Verse", "UEFN"]),
    dict(slug="tacline", name="Tacline", where="tacline.co",
         text="Airsoft platform: game discovery, field map, sign-ups and online payment.",
         tags=["Airsoft", "Payments"]),
]


def api(path):
    headers = {"Accept": "application/vnd.github+json"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request("https://api.github.com" + path, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as res:
        return json.load(res)


def compact(n):
    return f"{n / 1000:.1f}k".replace(".0k", "k") if n >= 1000 else str(n)


def live_stat(card):
    kind, repo = card.get("stat"), card.get("repo")
    try:
        if kind == "stars":
            stars = api(f"/repos/{repo}")["stargazers_count"]
            return "★ " + compact(stars) if stars else None
        if kind == "downloads":
            releases = api(f"/repos/{repo}/releases?per_page=100")
            return "↓ " + compact(sum(a["download_count"] for r in releases for a in r["assets"]))
    except Exception as err:
        print(f"{card['slug']}: live stat failed ({err}), using fallback")
    return card.get("fallback")


def merged_prs(repo):
    query = urllib.parse.quote(f"author:{LOGIN} is:pr is:merged repo:{repo}")
    return api(f"/search/issues?q={query}&per_page=1")["total_count"]


def chips_for(card):
    tags = list(card["tags"])
    if card.get("prs_repo"):
        try:
            tags.insert(0, f"{merged_prs(card['prs_repo'])} merged PRs")
        except Exception as err:
            print(f"{card['slug']}: PR count failed ({err})")
    return tags


def render(card, accent):
    lines = textwrap.wrap(card["text"], 48)
    if len(lines) > 2:
        raise SystemExit(f"{card['slug']}: text wraps to {len(lines)} lines, shorten it")
    body = [
        f'<rect x="0.5" y="14" width="3" height="{HEIGHT - 28}" rx="1.5" fill="{accent}"/>',
        f'<text x="20" y="26" font-size="10" fill="{MUTED}">{escape(card["where"])}</text>',
        f'<text x="20" y="48" font-size="16" font-weight="700" fill="{TITLE}">{escape(card["name"])}</text>',
    ]
    stat = live_stat(card)
    if stat:
        body.append(f'<text x="{WIDTH - 20}" y="26" font-size="11" font-weight="700" fill="{accent}" text-anchor="end">{escape(stat)}</text>')
    for i, line in enumerate(lines):
        body.append(f'<text x="20" y="{68 + i * 16}" font-size="12" fill="{TEXT}">{escape(line)}</text>')
    x = 20
    for tag in chips_for(card):
        w = len(tag) * 6.2 + 16
        body.append(
            f'<rect x="{x:.1f}" y="92" width="{w:.1f}" height="18" rx="9" fill="{CHIP}"/>'
            f'<text x="{x + w / 2:.1f}" y="105" font-size="10" fill="{MUTED}" text-anchor="middle">{escape(tag)}</text>'
        )
        x += w + 6
    return svg(WIDTH, HEIGHT, card["name"], "".join(body))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for i, card in enumerate(CARDS):
        (OUT / f"{card['slug']}.svg").write_text(render(card, PALETTE[i % len(PALETTE)]), encoding="utf-8")
    print(f"wrote {len(CARDS)} cards to assets/cards/")


if __name__ == "__main__":
    main()
