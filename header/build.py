"""Build the animated README header for github.com/anishfyi.

Each section of the header is its own SVG. Inside every SVG is a <foreignObject>
holding plain HTML and CSS, so the layout can use grid, container queries and
CSS animation, and still render through GitHub's image proxy. Every section is
written twice, once per colour scheme, and README.md picks between them with
<picture> and prefers-color-scheme.

The contribution graph is real: it is read from the GitHub GraphQL API. Run with
a token in GITHUB_TOKEN (the scheduled workflow passes its own):

    GITHUB_TOKEN=$(gh auth token) python3 header/build.py

Only the standard library is used, so the workflow needs no install step.
"""

from __future__ import annotations

import datetime as dt
import html
import json
import os
import pathlib
import urllib.request

LOGIN = "anishfyi"
OUT = pathlib.Path(__file__).resolve().parent
YEARS_SHOWN = 3

INTRO = (
    "I'm Anish. A backend and applied AI engineer in Gurugram, building the "
    "tools AI agents are missing and shipping them in the open."
)

# Link buttons, in the order they stack down the left of the header.
LINKS = [
    ("website", "Website"),
    ("velofy", "Velofy"),
    ("linkedin", "LinkedIn"),
    ("x", "X"),
    ("call", "Book a call"),
]

# Sage, taken from anishfyi.com: --accent is #bdcfb4 on dark and #365d3f on light.
THEMES = {
    "light": {
        "text": "#365d3f",
        "dots": ["#ecefea", "#c5d5c0", "#8fae8c", "#5f8564", "#365d3f"],
        "border": "rgb(0 0 0 / 0.05)",
        "shine": "rgb(255 255 255 / 0.55)",
    },
    "dark": {
        "text": "#bdcfb4",
        "dots": ["#161b1a", "#26352b", "#43604a", "#7e9c7a", "#bdcfb4"],
        "border": "rgb(255 255 255 / 0.03)",
        "shine": "rgb(255 255 255 / 0.5)",
    },
}

LEVELS = {
    "NONE": 0,
    "FIRST_QUARTILE": 1,
    "SECOND_QUARTILE": 2,
    "THIRD_QUARTILE": 3,
    "FOURTH_QUARTILE": 4,
}

FONT = (
    '-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans",Helvetica,Arial,'
    'sans-serif,"Apple Color Emoji","Segoe UI Emoji"'
)


# ---------------------------------------------------------------- data


def graphql(query: str, variables: dict) -> dict:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN is not set")
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        body = json.load(response)
    if body.get("errors"):
        raise SystemExit(f"GraphQL error: {body['errors']}")
    return body["data"]


YEARS_QUERY = """
query($login: String!) {
  user(login: $login) { contributionsCollection { contributionYears } }
}
"""

CALENDAR_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionLevel } }
      }
    }
  }
}
"""


def fetch(today: dt.date) -> tuple[int, list[tuple[int, list[tuple[dt.date, int]]]]]:
    """Return the all-time total and, per shown year, its days newest first."""
    years = graphql(YEARS_QUERY, {"login": LOGIN})["user"]["contributionsCollection"][
        "contributionYears"
    ]
    total = 0
    shown = []
    for year in sorted(years, reverse=True):
        start = dt.datetime(year, 1, 1)
        end = dt.datetime(year, 12, 31, 23, 59, 59)
        calendar = graphql(
            CALENDAR_QUERY,
            {"login": LOGIN, "from": start.isoformat() + "Z", "to": end.isoformat() + "Z"},
        )["user"]["contributionsCollection"]["contributionCalendar"]
        total += calendar["totalContributions"]
        if len(shown) < YEARS_SHOWN:
            days = [
                (dt.date.fromisoformat(day["date"]), LEVELS[day["contributionLevel"]])
                for week in calendar["weeks"]
                for day in week["contributionDays"]
            ]
            days = [d for d in days if d[0].year == year and d[0] <= today]
            days.sort(reverse=True)
            shown.append((year, days))
    return total, shown


# ---------------------------------------------------------------- svg


BASE_CSS = """
:root {
  --default-delay: 0.6s;
  --default-duration: 1.4s;
  --default-stagger: 0.1s;
  --menu-delay: calc(var(--default-delay) + var(--default-stagger) * 0);
  --links-delay: calc(var(--default-delay) + var(--default-stagger) * 1);
  --count-delay: calc(var(--default-delay) + var(--default-stagger) * 5);
  --readme-delay: calc(var(--default-delay) + var(--default-stagger) * 6);
  --copy-delay: calc(var(--default-delay) + var(--default-stagger) * 7);
  --graph-delay: calc(var(--default-delay) + var(--default-stagger) * 17);
}
*, *::before, *::after { box-sizing: border-box; }
p { margin: 0; }
.grid { display: grid; grid-template-columns: repeat(6, 1fr); }
.wrapper {
  contain: strict;
  block-size: calc(var(--size-height) * 1px);
  container-type: inline-size;
  position: relative;
  overflow: clip;
  font-family: FONT;
  color: var(--color-text);
}
.label { font-size: 14px; font-weight: 600; }
.link { font-size: 14px; display: flex; gap: 4px; }
.fade-in {
  animation: fade-in var(--duration, var(--default-duration)) var(--ease, ease-out)
    var(--delay, var(--default-delay)) both;
}
@keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }
.shine {
  background-color: var(--color-text);
  background-image: linear-gradient(-75deg, transparent 0%, var(--color-shine) 15%, transparent 25%);
  background-size: 200%;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: shine 14s infinite;
}
@keyframes shine { 0% { background-position: 200%; } 10%, 100% { background-position: 0%; } }
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; }
}
""".replace("FONT", FONT)


def theme_css(theme: str) -> str:
    t = THEMES[theme]
    dots = "".join(f"--color-dot-{i}: {c}; " for i, c in enumerate(t["dots"]))
    return (
        f":root {{ --color-text: {t['text']}; --color-shine: {t['shine']}; "
        f"--color-dot-border: {t['border']}; {dots}}}"
    )


def svg(theme: str, width: str, height: int, css: str, body: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" fill="none" width="{width}" height="{height}">'
        '<foreignObject width="100%" height="100%">'
        '<div xmlns="http://www.w3.org/1999/xhtml">'
        f"<style>{theme_css(theme)}{BASE_CSS}{css}</style>{body}"
        "</div></foreignObject></svg>\n"
    )


def compact(n: int) -> str:
    return f"{n / 1000:.1f}k".replace(".0k", "k") if n >= 1000 else str(n)


def top(theme: str, total: int) -> str:
    css = """
:root { --size-height: 20; }
.wrapper { align-items: center; }
.menu { --delay: var(--menu-delay); grid-area: 1 / 1 / span 1 / span 3; }
.count { --delay: var(--count-delay); grid-area: 1 / 4 / span 1 / span 2; display: none; }
.readme { --delay: var(--readme-delay); grid-area: 1 / 4 / span 1 / span 3; text-align: right; }
@container (width > 550px) {
  .count { display: block; grid-area: 1 / 3 / span 1 / span 2; }
  .readme { grid-area: 1 / 5 / span 1 / span 2; }
}
@container (width > 700px) {
  .count { grid-area: 1 / 4 / span 1 / span 2; }
  .readme { grid-area: 1 / 6 / span 1 / span 1; }
}
"""
    body = (
        '<div class="wrapper grid label">'
        '<div class="menu fade-in">Anish Kr Singh</div>'
        f'<div class="count fade-in"><span class="shine">{compact(total)}</span> Contributions</div>'
        '<div class="readme fade-in">readme.md</div>'
        "</div>"
    )
    return svg(theme, "100%", 20, css, body)


def link(theme: str, label: str, index: int) -> str:
    css = f"""
:root {{ --size-height: 18; }}
.wrapper {{ display: flex; align-items: center; }}
.link {{ --delay: calc(var(--links-delay) + var(--default-stagger) * {index}); }}
"""
    body = (
        '<div class="wrapper">'
        f'<div class="link fade-in"><span class="shine">{html.escape(label)}</span><span>↗</span></div>'
        "</div>"
    )
    return svg(theme, "110", 18, css, body)


def letters(text: str) -> str:
    return "".join(
        f'<span class="fade-in" style="--i: {i};">{html.escape(ch)}</span>'
        for i, ch in enumerate(text)
    )


DOT, GAP, ROWS, LABEL = 16, 4, 7, 20
GRAPH_HEIGHT = ROWS * DOT + (ROWS - 1) * GAP


def year_block(index: int, label: str, days: list[tuple[dt.date, int]]) -> tuple[str, int]:
    # Newest first. Rows run Saturday (top) to Sunday (bottom) so a column read
    # top-down walks back through one week; empty slots pad the first column.
    first = days[0][0]
    pad = 6 - (first.isoweekday() % 7)
    cells = ['<div class="dot dot--pad"></div>'] * pad
    cells += [f'<div class="dot dot--{level}"></div>' for _, level in days]
    columns = -(-len(cells) // ROWS)
    width = columns * DOT + (columns - 1) * GAP
    block = (
        f'<div class="year" style="--w: {width};">'
        f'<div class="year__days">{"".join(cells)}</div>'
        f'<div class="year__label label"><span>{label}</span></div>'
        "</div>"
    )
    return block, width


def main(theme: str, today: dt.date, shown) -> str:
    blocks, widths = [], []
    for index, (year, days) in enumerate(shown):
        if not days:
            continue
        label = today.strftime("%b %-d, %Y") if index == 0 else str(year)
        block, width = year_block(index, label, days)
        blocks.append(block)
        widths.append(width)
    year_gap = 24
    total_width = sum(widths) + year_gap * (len(widths) - 1)
    css = f"""
:root {{ --size-height: 290; --dot: {DOT}px; --gap: {GAP}px; }}
.wrapper {{ align-items: end; grid-template-rows: 1fr auto; row-gap: 20px; }}
.intro {{ grid-area: 1 / 1 / span 1 / span 6; font-size: 18px; font-weight: 300; line-height: 1.35; }}
.intro span {{ --duration: 980ms; --delay: calc(var(--copy-delay) + var(--i) * 10ms); }}
@container (width > 550px) {{ .intro {{ grid-area: 1 / 3 / span 1 / span 4; font-size: 22px; }} }}
@container (width > 700px) {{ .intro {{ grid-area: 1 / 4 / span 1 / span 3; }} }}
.graph {{ grid-area: 2 / 1 / span 1 / span 6; --delay: var(--graph-delay); }}
.years {{
  display: flex;
  gap: {year_gap}px;
  inline-size: {total_width}px;
  will-change: transform;
  animation: scroll {30 + total_width * 0.03:.0f}s ease-in-out 3s infinite alternate;
}}
@keyframes scroll {{
  0%, 6% {{ transform: translateX(0); }}
  94%, 100% {{ transform: translateX(min(0px, calc(100cqw - 100%))); }}
}}
.year {{ flex: none; inline-size: calc(var(--w) * 1px); }}
.year__days {{
  display: grid;
  grid-auto-flow: column;
  grid-template-rows: repeat({ROWS}, var(--dot));
  grid-auto-columns: var(--dot);
  gap: var(--gap);
  block-size: {GRAPH_HEIGHT}px;
}}
.year__label {{ block-size: {LABEL}px; display: flex; align-items: end; }}
.dot {{
  border: 1px solid var(--color-dot-border);
  border-radius: 3px;
}}
.dot--pad {{ visibility: hidden; }}
.dot--0 {{ background: var(--color-dot-0); }}
.dot--1 {{ background: var(--color-dot-1); }}
.dot--2 {{ background: var(--color-dot-2); }}
.dot--3 {{ background: var(--color-dot-3); }}
.dot--4 {{ background: var(--color-dot-4); }}
"""
    body = (
        '<main class="wrapper grid">'
        f'<article class="intro"><p>{letters(INTRO)}</p></article>'
        f'<article class="graph fade-in"><div class="years">{"".join(blocks)}</div></article>'
        "</main>"
    )
    return svg(theme, "100%", 290, css, body)


def build(today: dt.date | None = None) -> None:
    today = today or dt.datetime.now(dt.timezone.utc).date()
    total, shown = fetch(today)
    for theme in THEMES:
        (OUT / f"top-{theme}.svg").write_text(top(theme, total))
        for index, (slug, label) in enumerate(LINKS):
            (OUT / f"link-{slug}-{theme}.svg").write_text(link(theme, label, index))
        (OUT / f"main-{theme}.svg").write_text(main(theme, today, shown))
    print(f"{total} contributions, {len(shown)} years drawn, written to {OUT}")


if __name__ == "__main__":
    build()
