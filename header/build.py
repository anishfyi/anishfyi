"""Build the README header for github.com/anishfyi.

The header reads as one panel in the Foundry style of velofy.co: a black ground
in dark mode and warm paper in light mode, cream text, one gold accent, Switzer
at regular weight and Fragment Mono for small labels. It is a stack of SVG files:

    hero      the name set large, a mono label row and a short intro
    link-*    six text links with arrows, three to a row
    graph     three years of contributions as gold cells at rising opacity

Every piece is checked from a 278px column (a 360px phone: GitHub's 16px page
gutters and the profile card's 24px padding come off each side) up to 900px.

Each SVG holds a <foreignObject> with plain HTML and CSS and is written twice,
once per colour scheme; README.md picks one with <picture> and
prefers-color-scheme. The images sit inline with align="top" rather than
floated, because GitHub pads floated README images by 20px, which would cut
gaps into the panel.

GitHub serves README images as <img>, which cannot load anything external, so
the fonts are embedded as base64 data URIs. They are fetched at build time and
never committed as font files: Switzer from velofy.co (ITF Free Font License,
embedded unmodified for the owner's own use) and Fragment Mono from the jsDelivr
CDN (SIL Open Font License). If a fetch fails, the copy embedded by the previous build is
reused, so the daily refresh does not depend on either host being up.

The contribution graph is real: it is read from the GitHub GraphQL API. Run with
a token in GITHUB_TOKEN (the scheduled workflow passes its own):

    GITHUB_TOKEN=$(gh auth token) python3 header/build.py

Only the standard library is used, so the workflow needs no install step.
"""

from __future__ import annotations

import base64
import datetime as dt
import functools
import html
import json
import os
import pathlib
import re
import urllib.request

LOGIN = "anishfyi"
OUT = pathlib.Path(__file__).resolve().parent
YEARS_SHOWN = 3

# The README column on a profile page is about 830px wide. Paddings are fractions
# of the panel width so every piece lines up at any width; text stays in px.
DESIGN_WIDTH = 830
PAD = 32 / DESIGN_WIDTH
COLUMN_GAP = 16 / DESIGN_WIDTH

NAME = "Anish Kr Singh"
INTRO = (
    "I build backend systems and tools for artificial intelligence (AI), and I "
    "co-founded Velofy, an applied AI and security lab in Delhi."
)
LABEL_LEFT = "README.MD"
LABEL_RIGHT = "Gurugram, India"

# (slug, label). Three to a row; README.md holds the matching links.
LINKS = [
    ("site", "anishfyi.com"),
    ("velofy", "Velofy"),
    ("linkedin", "LinkedIn"),
    ("x", "X"),
    ("call", "Book a call"),
    ("email", "Email"),
]

# README.md declares these heights (and GRAPH_HEIGHT) on its <img> tags; keep them in step.
HERO_HEIGHT = 290
LINK_HEIGHT = 52

# Foundry tokens from velofy.co. Contribution cells are the accent at rising opacity.
THEMES = {
    "dark": {
        "paper": "#000000",
        "ink": "#e6dec7",
        "muted": "#9c9686",
        "accent": "#c8ad86",
        "line": "#2f2c27",
        "cell": "200 173 134",
        "levels": [0.14, 0.34, 0.56, 0.78, 1.0],
    },
    "light": {
        "paper": "#f5efe0",
        "ink": "#17140e",
        "muted": "#5f5849",
        "accent": "#765a33",
        "line": "#d6ccb4",
        "cell": "118 90 51",
        "levels": [0.1, 0.3, 0.52, 0.76, 1.0],
    },
}

LEVELS = {
    "NONE": 0,
    "FIRST_QUARTILE": 1,
    "SECOND_QUARTILE": 2,
    "THIRD_QUARTILE": 3,
    "FOURTH_QUARTILE": 4,
}

FONTS = {
    "switzer-400": ("Switzer", 400, "https://velofy.co/fonts/switzer/switzer-400.woff2"),
    "switzer-500": ("Switzer", 500, "https://velofy.co/fonts/switzer/switzer-500.woff2"),
    "mono": (
        "Fragment Mono",
        400,
        "https://cdn.jsdelivr.net/npm/@fontsource/fragment-mono@5.2.8/files/"
        "fragment-mono-latin-400-normal.woff2",
    ),
}

SANS = 'Switzer,"Helvetica Neue",Arial,sans-serif'
MONO = '"Fragment Mono",ui-monospace,Menlo,monospace'

# The Velofy "module V" mark, viewBox 0 0 100 100 (velofyMarkPath in the site's brand.mjs).
VELOFY_MARK = (
    "M43.62 84.6Q41.6 84.6 41.6 82.58L41.6 72.9Q41.6 70.89 40.18 69.46L38.93 68.22Q37.51 66.79 "
    "35.49 66.79L25.82 66.79Q23.8 66.79 23.8 64.78L23.8 46.71Q23.8 44.69 22.38 43.27L21.13 42.02Q19.71 "
    "40.6 17.69 40.6L8.02 40.6Q6 40.6 6 38.58L6 17.42Q6 15.4 8.02 15.4L20.78 15.4Q22.79 15.4 22.79 "
    "17.42L22.79 35.49Q22.79 37.51 24.22 38.93L25.46 40.18Q26.89 41.6 28.9 41.6L38.58 41.6Q40.6 41.6 "
    "40.6 43.62L40.6 61.69Q40.6 63.71 42.02 65.13L43.27 66.38Q44.69 67.8 46.71 67.8L53.29 67.8Q55.31 "
    "67.8 56.73 66.38L57.98 65.13Q59.4 63.71 59.4 61.69L59.4 43.62Q59.4 41.6 61.42 41.6L71.1 41.6Q73.11 "
    "41.6 74.54 40.18L75.78 38.93Q77.21 37.51 77.21 35.49L77.21 17.42Q77.21 15.4 79.22 15.4L91.98 "
    "15.4Q94 15.4 94 17.42L94 38.58Q94 40.6 91.98 40.6L82.31 40.6Q80.29 40.6 78.87 42.02L77.62 "
    "43.27Q76.2 44.69 76.2 46.71L76.2 64.78Q76.2 66.79 74.18 66.79L64.51 66.79Q62.49 66.79 61.07 "
    "68.22L59.82 69.46Q58.4 70.89 58.4 72.9L58.4 82.58Q58.4 84.6 56.38 84.6L43.62 84.6Z"
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


def fetch(today: dt.date) -> tuple[int, int, list[tuple[int, int, dict[dt.date, int]]]]:
    """Return the all-time total, the first year, and per shown year its total and levels."""
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
            levels = {
                dt.date.fromisoformat(day["date"]): LEVELS[day["contributionLevel"]]
                for week in calendar["weeks"]
                for day in week["contributionDays"]
            }
            levels = {d: v for d, v in levels.items() if d.year == year and d <= today}
            shown.append((year, calendar["totalContributions"], levels))
    return total, min(years), shown


# ---------------------------------------------------------------- fonts


@functools.cache
def font_base64(key: str) -> str:
    _, _, url = FONTS[key]
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "anishfyi-readme-header"})
        with urllib.request.urlopen(request, timeout=30) as response:
            data = response.read()
        if data[:4] == b"wOF2":
            return base64.b64encode(data).decode()
    except OSError:
        pass
    # The host is down or changed: reuse the copy the previous build embedded.
    pattern = re.compile(r"/\*font:" + re.escape(key) + r"\*/[^}]*?base64,([A-Za-z0-9+/=]+)")
    for path in sorted(OUT.glob("*.svg")):
        match = pattern.search(path.read_text())
        if match:
            return match.group(1)
    raise SystemExit(f"Could not load the {key} font from {url} or a previous build")


def font_face(key: str) -> str:
    family, weight, _ = FONTS[key]
    return (
        f"/*font:{key}*/@font-face{{font-family:\"{family}\";font-weight:{weight};"
        f"font-style:normal;font-display:block;"
        f"src:url(data:font/woff2;base64,{font_base64(key)}) format(\"woff2\")}}"
    )


# ---------------------------------------------------------------- svg

BASE_CSS = f"""
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
.root{{width:100%;height:100%;container-type:inline-size}}
.panel{{position:relative;width:100%;height:100%;overflow:hidden;background:var(--paper);
  color:var(--ink);font:400 16px/1.3 {SANS};-webkit-font-smoothing:antialiased;
  -moz-osx-font-smoothing:grayscale;text-rendering:geometricPrecision}}
.mono{{font:400 12px/1 {MONO};letter-spacing:.04em;text-transform:uppercase;white-space:nowrap;color:var(--muted)}}
.gold{{color:var(--accent)}}
.in{{animation:in 1.2s cubic-bezier(.2,.7,.2,1) var(--d,0s) both}}
@keyframes in{{from{{opacity:0}}to{{opacity:1}}}}
@media (prefers-reduced-motion:reduce){{*,*::before,*::after{{animation:none!important}}}}
"""


def tokens(theme: str) -> str:
    t = THEMES[theme]
    cells = "".join(
        f"--l{i}:rgb({t['cell']} / {alpha});" for i, alpha in enumerate(t["levels"])
    )
    names = ("paper", "ink", "muted", "accent", "line")
    return ":root{" + "".join(f"--{k}:{t[k]};" for k in names) + cells + "}"


def svg(theme: str, css: str, body: str, fonts: tuple[str, ...], height: int) -> str:
    """Wrap HTML in an SVG as wide as its <img> and a fixed number of pixels tall.

    The layout inside responds to the width with container queries. A viewBox that
    scales the whole picture is avoided: Safari does not scale <foreignObject>
    content with the viewBox when the SVG is drawn as an image.
    """
    faces = "".join(font_face(key) for key in fonts)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="{height}" fill="none">'
        '<foreignObject width="100%" height="100%">'
        '<div xmlns="http://www.w3.org/1999/xhtml" class="root">'
        f"<style><![CDATA[{faces}{tokens(theme)}{BASE_CSS}{css}]]></style>{body}"
        "</div></foreignObject></svg>\n"
    )


def cqw(fraction: float) -> str:
    return f"{fraction * 100:.4f}cqw"


def hero(theme: str) -> str:
    # At -0.028em tracking the name measures about 6.06em in Switzer, so 6.08 fills
    # the column on one line with a hair to spare for kerning differences between
    # browsers. It stops growing at 128px (an 845px column) so the intro keeps its
    # distance in wider README columns. Below 600px it breaks onto two lines and shrinks with the width, so
    # the name and a four-line intro still fit the fixed height on a 360px phone
    # (a 278px README column). The name's bottom margin keeps the intro clear of
    # the descender in "Singh" when the panel is full.
    first, rest = NAME.split(" ", 1)
    css = f"""
.hero{{--pad:{cqw(PAD)};display:flex;flex-direction:column;padding:28px var(--pad) 30px;border-radius:4px 4px 0 0}}
.bar{{display:flex;justify-content:space-between;gap:16px}}
.name{{margin:28px 0 16px -.02em;font:400 min(128px, calc((100cqw - 2 * var(--pad)) / 6.08))/.86 {SANS};
  letter-spacing:-.028em;white-space:nowrap;color:var(--ink)}}
.name span,.nw{{white-space:nowrap}}
.intro{{margin-top:auto;max-width:30em;font-size:20px;line-height:1.3;letter-spacing:-.01em}}
@container (width < 600px){{
  .hero{{padding-top:22px;padding-bottom:22px}}
  .name{{margin-top:20px;font-size:min(68px, 18.5cqw);line-height:.88;white-space:normal}}
  .intro{{font-size:16px;line-height:1.35}}
}}
"""
    # Keep "co-founded" whole so a narrow column does not break it at the hyphen.
    intro = html.escape(INTRO).replace("co-founded", '<span class="nw">co-founded</span>')
    body = (
        '<div class="panel hero">'
        f'<div class="bar mono in" style="--d:.05s"><span class="gold">{html.escape(LABEL_LEFT)}</span>'
        f"<span>{html.escape(LABEL_RIGHT)}</span></div>"
        f'<div class="name in" style="--d:.15s"><span>{html.escape(first)}</span> '
        f"<span>{html.escape(rest)}</span></div>"
        f'<p class="intro in" style="--d:.4s">{intro}</p>'
        "</div>"
    )
    return svg(theme, css, body, ("switzer-400", "mono"), HERO_HEIGHT)


ARROW = (
    '<svg xmlns="http://www.w3.org/2000/svg" class="arrow" viewBox="0 0 12 12" aria-hidden="true">'
    '<path d="M3 9 9 3M4 3h5v5" fill="none" stroke="currentColor" stroke-width="1.35" '
    'stroke-linecap="round" stroke-linejoin="round"/></svg>'
)
MARK = (
    '<svg xmlns="http://www.w3.org/2000/svg" class="mark" viewBox="0 0 100 100" aria-hidden="true">'
    f'<path d="{VELOFY_MARK}" fill="currentColor"/></svg>'
)


def link(theme: str, index: int, slug: str, label: str) -> str:
    # Each cell is a third of the panel. The three text columns share the panel's
    # padding and a 16px gap, so the column edges line up with the hero and graph.
    column = (1 - 2 * PAD - 2 * COLUMN_GAP) / 3
    position = index % 3
    start = PAD + position * (column + COLUMN_GAP) - position / 3
    css = f"""
.col{{position:absolute;top:0;bottom:0;left:{cqw(start * 3)};width:{cqw(column * 3)};
  display:flex;align-items:center;gap:5px;border-top:1px solid var(--line);
  font:500 16px/1 {SANS};letter-spacing:-.01em;white-space:nowrap}}
.arrow{{width:12px;height:12px;flex:none;margin-top:1px}}
.mark{{width:15px;height:15px;flex:none;color:var(--accent);margin-right:1px}}
@container (width < 170px){{.col{{font-size:13px;gap:4px}}.arrow{{width:10px;height:10px}}.mark{{width:12px;height:12px}}}}
@container (width < 100px){{.col{{font-size:12px;gap:3px;letter-spacing:-.02em}}.arrow{{width:9px;height:9px}}.mark{{width:11px;height:11px}}}}
@container (width < 92px){{.arrow{{display:none}}}}
"""
    mark = MARK if slug == "velofy" else ""
    body = (
        '<div class="panel">'
        f'<div class="col in" style="--d:{0.5 + index * 0.07:.2f}s">{mark}'
        f"<span>{html.escape(label)}</span>{ARROW}</div>"
        "</div>"
    )
    return svg(theme, css, body, ("switzer-500",), LINK_HEIGHT)


# Each year is a strip of week columns. --p is the pitch (cell plus gap): 10px
# when there is room, shrinking to fit narrower columns; the graph keeps the same
# height at every width. Above 720px cells are 80% of the pitch. Below it the
# cell and gap are rounded to whole pixels, because fractional cells of 3 to 6px
# blur into stripes; below 400px the year labels move above the strips so each
# strip gets the full width, and the pitch is capped at 5px so three strips fit.
GRAPH_HEIGHT = 298
SIDE, LABEL, LABEL_GAP, SIDE_GAP = 164, 48, 18, 24


def weeks(year: int) -> int:
    """How many week columns the year spans: 53 for most years, 54 for a few."""
    offset = dt.date(year, 1, 1).isoweekday() % 7
    days = (dt.date(year + 1, 1, 1) - dt.date(year, 1, 1)).days
    return -(-(offset + days) // 7)


def strip(year: int, levels: dict[dt.date, int]) -> str:
    # Columns are weeks starting on Sunday, rows run Sunday to Saturday, as on GitHub.
    first = dt.date(year, 1, 1)
    cells = ['<i class="x"></i>'] * (first.isoweekday() % 7)
    cells += [f'<i class="l{levels[day]}"></i>' for day in sorted(levels)]
    return "".join(cells)


def graph(theme: str, today: dt.date, total: int, since: int, shown) -> str:
    rows = [(year, count, levels) for year, count, levels in shown if levels]
    label = LABEL + LABEL_GAP
    n = max(weeks(year) for year, _, _ in rows)
    span = n - 0.2  # strip width in pitches: n cells of .8 and n - 1 gaps of .2
    css = f"""
.graph{{--pad:{cqw(PAD)};display:flex;gap:{SIDE_GAP}px;padding:30px var(--pad) 32px;border-radius:0 0 4px 4px}}
.graph::before{{content:"";position:absolute;top:0;left:var(--pad);right:var(--pad);border-top:1px solid var(--line)}}
.side{{flex:none;width:{SIDE}px;display:flex;flex-direction:column}}
.total{{margin-top:14px;font:400 44px/1 {SANS};letter-spacing:-.025em;color:var(--ink)}}
.since{{margin-top:12px}}
.foot{{margin-top:auto;display:flex;flex-direction:column;gap:12px}}
.legend{{display:flex;align-items:center;gap:6px}}
.legend .cells{{display:flex;gap:2px}}
.legend i{{width:8px;height:8px;border-radius:2px}}
.years{{flex:1;min-width:0;display:flex;flex-direction:column;gap:16px;
  --p:min(10px, calc((100cqw - 2 * var(--pad) - {SIDE + SIDE_GAP + label}px) / {span:g}))}}
.year{{display:flex;gap:{LABEL_GAP}px;justify-content:flex-end}}
.label{{flex:none;width:{LABEL}px;display:flex;flex-direction:column;gap:8px}}
.days{{--c:calc(var(--p) * .8);--g:calc(var(--p) * .2);flex:none;display:grid;grid-auto-flow:column;
  grid-template-rows:repeat(7,var(--c));grid-auto-columns:var(--c);gap:var(--g);
  width:calc(var(--c) * {n} + var(--g) * {n - 1});height:calc(var(--c) * 7 + var(--g) * 6);
  animation:wipe 1.8s cubic-bezier(.3,.6,.2,1) var(--d,0s) both}}
@keyframes wipe{{from{{clip-path:inset(0 100% 0 0)}}to{{clip-path:inset(0 0 0 0)}}}}
i{{display:block;border-radius:calc(var(--c) * .28)}}
.x{{visibility:hidden}}
.l0{{background:var(--l0)}}.l1{{background:var(--l1)}}.l2{{background:var(--l2)}}
.l3{{background:var(--l3)}}.l4{{background:var(--l4)}}
@container (width < 720px){{
  .graph{{flex-direction:column;gap:18px;padding:24px var(--pad) 26px}}
  .side{{width:auto;flex-direction:row;align-items:baseline;gap:12px}}
  .total{{margin:0;font-size:28px}}
  .since{{margin:0 0 0 auto}}
  .foot{{display:none}}
  .years{{justify-content:center;gap:12px;
    --p:min(8.6px, calc((100cqw - 2 * var(--pad) - {label}px) / {span:g}))}}
  .year{{justify-content:flex-start}}
}}
@container (width < 400px){{
  .graph{{padding:22px var(--pad) 20px}}
  .side{{display:grid;grid-template-columns:1fr auto;align-items:baseline;gap:10px 12px}}
  .side>.gold{{grid-area:1/1}}
  .since{{grid-area:1/2;margin:0}}
  .total{{grid-area:2/1/3/3;font-size:36px}}
  .years{{--p:min(5px, calc((100cqw - 2 * var(--pad)) / {span:g}))}}
  .year{{flex-direction:column;gap:6px}}
  .label{{width:auto;flex-direction:row;gap:10px}}
}}
@supports (width:round(down, 5.5px, 1px)){{
  @container (width < 720px){{
    .days{{--g:max(1px, round(var(--p) * .2, 1px));--c:round(down, var(--p) - var(--g), 1px)}}
  }}
}}
"""
    years_html = "".join(
        f'<div class="year"><div class="label in" style="--d:{0.9 + i * 0.15:.2f}s">'
        f'<span class="mono gold">{year}</span><span class="mono">{count:,}</span></div>'
        f'<div class="days" style="--d:{0.9 + i * 0.15:.2f}s">{strip(year, levels)}</div></div>'
        for i, (year, count, levels) in enumerate(rows)
    )
    legend = "".join(f'<i class="l{i}"></i>' for i in range(5))
    body = (
        '<div class="panel graph">'
        '<div class="side in" style="--d:.8s">'
        '<p class="mono gold">Contributions</p>'
        f'<p class="total">{total:,}</p>'
        f'<p class="mono since">Since {since}</p>'
        '<div class="foot">'
        f'<div class="mono legend">Less<span class="cells">{legend}</span>More</div>'
        f'<p class="mono">Updated {today.day} {today.strftime("%b %Y")}</p>'
        "</div></div>"
        f'<div class="years">{years_html}</div>'
        "</div>"
    )
    return svg(theme, css, body, ("switzer-400", "mono"), GRAPH_HEIGHT)


def build(today: dt.date | None = None) -> None:
    today = today or dt.datetime.now(dt.timezone.utc).date()
    total, since, shown = fetch(today)
    for theme in THEMES:
        (OUT / f"hero-{theme}.svg").write_text(hero(theme))
        for index, (slug, label) in enumerate(LINKS):
            (OUT / f"link-{slug}-{theme}.svg").write_text(link(theme, index, slug, label))
        (OUT / f"graph-{theme}.svg").write_text(graph(theme, today, total, since, shown))
    print(f"{total} contributions since {since}, {len(shown)} years drawn, written to {OUT}")


if __name__ == "__main__":
    build()
