"""Updates the dynamic parts of README.md from data/*.json.

- the latest-articles block between <!-- writing:start --> and <!-- writing:end -->
  (links + alt text; the images themselves come from render.py)
- the alt text of the stats image, so screen readers get today's numbers

Everything else in the README is left exactly as it is.
"""
import datetime
import hashlib
import html
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
README = HERE.parent.parent / "README.md"
DATA = HERE / "data"


def writing_block(articles):
    lines = []
    for i, a in enumerate(articles[:5], 1):
        alt = html.escape(f'{a["title"]} — published {a["published_at"][:10]}, '
                          f'{a["reactions"]} reactions, {a["comments"]} comments', quote=True)
        lines.append(f'<a href="{html.escape(a["url"], quote=True)}"><img src="./assets/writing/post-{i}.svg" '
                     f'width="100%" align="top" alt="{alt}"></a>')
    return "<!-- writing:start -->\n" + "\n".join(lines) + "\n<!-- writing:end -->"


def days(n):
    return f"{n} day" if n == 1 else f"{n} days"


def stats_alt(d):
    since = datetime.date.fromisoformat(d["created_at"][:10])
    langs = sorted(d["languages"].items(), key=lambda kv: -kv[1])[:5]
    parts = [f'{d["stars"]} total stars',
             (f'{d["contributions_year"]} contributions in {d["year"]}, {d["contributions_all"]} all time'
              if "contributions_year" in d else f'{d["commits_year"]} commits in {d["year"]}, {d["commits_all"]} all time'),
             f'{d["prs"]} pull requests ({d["prs_merged"]} merged)',
             f'current streak {days(d["streak_current"])}, longest {days(d["streak_longest"])}',
             f'{d["followers"]} followers', f'{d["forks"]} forks',
             f'member since {since:%B %Y}']
    text = "Stats: " + "; ".join(parts) + ". Top languages: " + ", ".join(k for k, _ in langs) + "."
    dev = {k: v for k, v in (d.get("dev") or {}).items() if v is not None}
    if dev:
        text += " DEV Community: " + ", ".join(f"{v:,} {k}" for k, v in dev.items()) + "."
    return html.escape(text, quote=True)


def city_alt(calendar):
    total = sum(n for _, n in calendar)
    busiest = max(calendar, key=lambda t: t[1]) if calendar else None
    text = (f"Contribution city: an isometric night skyline with one building per day of the last year. "
            f"{total:,} contributions")
    if busiest and busiest[1]:
        d = datetime.date.fromisoformat(busiest[0])
        text += f", busiest day {d:%B} {d.day} with {busiest[1]}"
    return html.escape(text + ".", quote=True)


def main():
    stats = json.loads((DATA / "stats.json").read_text())
    s = README.read_text()
    # Publish a content-addressed header URL. A changed SVG receives a new
    # filename, avoiding GitHub's cached image proxy without relying on
    # query parameters or a commit-SHA reference that cannot be known yet.
    header = HERE.parent.parent / "assets" / "header.svg"
    header_bytes = header.read_bytes()
    digest = hashlib.sha256(header_bytes).hexdigest()[:16]
    versioned_name = f"header-{digest}.svg"
    versioned_header = header.with_name(versioned_name)
    if not versioned_header.exists() or versioned_header.read_bytes() != header_bytes:
        versioned_header.write_bytes(header_bytes)
    header_url = f"https://raw.githubusercontent.com/Big2What-Mods/Big2What-Mods/main/assets/{versioned_name}"
    s, header_count = re.subn(
        r'(<img\s+src=")[^"]*/assets/header(?:-[a-f0-9]{16})?\.svg(?:\?[^"]*)?(")',
        lambda m: m.group(1) + header_url + m.group(2),
        s,
    )
    if header_count != 1:
        sys.exit("error: README needs exactly one header SVG image")

    s, n = re.subn(r'(<img src="\./assets/stats\.svg"[^>]*?alt=")[^"]*(")',
                   lambda m: m.group(1) + stats_alt(stats) + m.group(2), s)
    if n != 1:
        sys.exit("error: README needs exactly one stats.svg image with an alt attribute")

    cal_file = DATA / "calendar.json"
    if cal_file.exists():   # optional section: only touched when the README has the city image
        s = re.sub(r'(<img src="\./assets/contribution-city\.svg"[^>]*?alt=")[^"]*(")',
                   lambda mm: mm.group(1) + city_alt(json.loads(cal_file.read_text())) + mm.group(2), s)

    README.write_text(s)
    print("README updated")


if __name__ == "__main__":
    main()
