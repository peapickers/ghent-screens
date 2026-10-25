#!/usr/bin/env python3
"""Write feed.xml (RSS 2.0) for the public GitHub Pages site.
One item per day for the next 7 days: every film, rarest first, with venue, times and who paid.
Usage: SITE_URL=https://<user>.github.io/ghent-screens python3 build_feed.py
Free software only: Python standard library."""
import json, os, datetime, zoneinfo, html
from email.utils import format_datetime

SITE = os.environ.get("SITE_URL", "https://example.github.io/ghent-screens").rstrip("/")
TZ = zoneinfo.ZoneInfo("Europe/Brussels")
D = json.load(open("screenings.json", encoding="utf-8"))
FILMS = {}
if os.path.exists("films.json"):
    for f in json.load(open("films.json", encoding="utf-8"))["films"]:
        for m in f["match"]:
            FILMS[m.lower()] = f
V = D["venues"]
today = datetime.datetime.now(TZ).date()
end = today + datetime.timedelta(days=6)
week = [s for s in D["screenings"] if today.isoformat() <= s["d"] <= end.isoformat()]
fid = lambda s: FILMS[s["title"].lower()]["id"] if s["title"].lower() in FILMS else s["title"].lower()
count = {}
for s in week:
    count[fid(s)] = count.get(fid(s), 0) + 1

items = []
for i in range(7):
    day = today + datetime.timedelta(days=i)
    rows = [s for s in week if s["d"] == day.isoformat()]
    if not rows:
        continue
    films = {}
    for s in rows:
        f = films.setdefault(fid(s), {"s": s, "venues": {}})
        f["venues"].setdefault(V[s["v"]]["name"], []).append(s["t"] or "time on site")
    order = sorted(films.items(), key=lambda kv: (count[kv[0]], kv[1]["s"]["t"] or "99"))
    body = ["<ol>"]
    for k, f in order:
        meta = FILMS.get(f["s"]["title"].lower())
        title = meta["title"] if meta else f["s"]["title"]
        where = "; ".join(f"{v} {' · '.join(sorted(ts))}" for v, ts in f["venues"].items())
        money = f"<br><small>Funding: {html.escape(meta['funding'])}</small>" if meta else ""
        body.append(f"<li><b>{html.escape(title)}</b> ({count[k]}× this week): {html.escape(where)}{money}</li>")
    body.append("</ol>")
    pub = datetime.datetime.combine(day, datetime.time(7, 0), TZ)
    items.append(f"""<item><title>two-step · {day.strftime('%A %-d %B')} · {len(films)} films</title>
<link>{SITE}/#{day.isoformat()}</link><guid isPermaLink="false">ghent-screens-{day.isoformat()}-{D['updated']}</guid>
<pubDate>{format_datetime(pub)}</pubDate><description><![CDATA[{''.join(body)}]]></description></item>""")

now = format_datetime(datetime.datetime.now(TZ))
xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>
<title>two-step</title><link>{SITE}/</link>
<atom:link href="{SITE}/feed.xml" rel="self" type="application/rss+xml"/>
<description>Daily screenings at Ghent's arthouse cinemas and film clubs, rarest films first, with who paid for each film. Kinepolis not included.</description>
<language>en</language><lastBuildDate>{now}</lastBuildDate>
{''.join(items)}
</channel></rss>"""
open("feed.xml", "w", encoding="utf-8").write(xml)
print(f"feed.xml: {len(items)} days")
