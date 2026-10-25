#!/usr/bin/env python3
"""Weekly automatic update of the film listings (wave 1: Sphinx, Studio Skoop, KASKcinema, Ciné Rio).

Runs in GitHub Actions without Claude. Reads only each venue's official programme page,
keeps only facts (date, time, title, short label, link; no images, no descriptions), and
merges them into screenings.json:
- a venue that parses fine: its listings from today on are replaced by the fresh ones;
- a venue that fails or returns nothing: its last known listings stay, and a notice says so.
Robots.txt of all four sites allows these pages (checked 25-10-2026).

Usage: python3 scripts/update_films.py            (fetch live)
       python3 scripts/update_films.py --dir DUMP (parse saved pages DUMP/<venue>.html)
Python standard library only."""
import datetime, html, json, re, sys, urllib.request, zoneinfo

TZ = zoneinfo.ZoneInfo("Europe/Brussels")
TODAY = datetime.datetime.now(TZ).date()
UA = "TwoStepBot/1.0 (+https://peapickers.github.io/two-step/; weekly, programme facts only)"
MONTHS = {m: i + 1 for i, m in enumerate("januari februari maart april mei juni juli augustus september oktober november december".split())}
AUTO = "Automatic update (film):"

SOURCES = {
    "sphinx": "https://www.sphinx-cinema.be/programma",
    "skoop": "https://www.studioskoop.be/agenda-studio-skoop/",
    "kask": "https://kaskcinema.be/",
    "rio": "https://dekoer.be/cine-rio/",
}


def text(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def year_for(month, day):
    """Dates on Sphinx, Skoop and Rio have no year: pick the one closest after today (allowing a week back)."""
    for y in (TODAY.year - 1, TODAY.year, TODAY.year + 1):
        try:
            d = datetime.date(y, month, day)
        except ValueError:
            continue
        if d >= TODAY - datetime.timedelta(days=7) and d <= TODAY + datetime.timedelta(days=330):
            return d
    return None


def row(v, d, t, title, note, url):
    title = title.replace("\u2019", "'").replace("\u2018", "'").strip()
    return {"v": v, "d": d.isoformat(), "t": t, "title": title, "note": note.strip(), "url": url, "k": "film", "city": "Gent"}


def parse_sphinx(h):
    out, url = [], SOURCES["sphinx"]
    for block in re.split(r'<div class="component-screenings__row">', h)[1:]:
        m = re.search(r"<h2>\s*\w+\s+(\d{1,2})\s+([a-z]+)\s*</h2>", block)
        if not m or m.group(2) not in MONTHS:
            continue
        d = year_for(MONTHS[m.group(2)], int(m.group(1)))
        if not d:
            continue
        for f in re.split(r'<div class="component-screenings--slot__film">', block)[1:]:
            t = re.search(r'component-screenings__time">\s*(\d{1,2}:\d{2})', f)
            ti = re.search(r'component-screenings__title">\s*<a[^>]*>(.*?)</a>', f, re.S)
            lab = re.search(r'component-screenings__label"><a[^>]*>(.*?)</a>', f, re.S)
            if t and ti:
                out.append(row("sphinx", d, t.group(1).zfill(5), text(ti.group(1)), text(lab.group(1)) if lab else "", url))
    return out


def parse_skoop(h):
    out, url = [], SOURCES["skoop"]
    for show in re.split(r'<div class="show col-', h)[1:]:
        tags = [text(x).lower() for x in re.findall(r"<span class='movietag[^']*'>(.*?)</span>", show)]
        for ev in re.findall(r'data-event="([^"]+)"', show):
            try:
                e = json.loads(html.unescape(ev))
                d = datetime.datetime.strptime(e["show_date"], "%d-%m-%Y").date()
                out.append(row("skoop", d, e["show_time"], e["film_name"], ", ".join(tags), url))
            except (ValueError, KeyError):
                continue
    return out


def parse_kask(h):
    out = []
    for b in re.findall(r'<div[^>]*class="film-list[^"]*">(.*?)</div>', h, re.S):
        u = re.search(r'<a href="([^"]+)"', b)
        d = re.search(r'datetime="(\d{4}-\d{2}-\d{2})"', b)
        t = re.search(r"–\s*(\d{1,2}:\d{2})", b)
        ti = re.search(r'<span class="film-title">(.*?)</span>\s*</a>', b, re.S)
        if not (u and d and ti):
            continue
        title = text(ti.group(1).replace('<span class="jaartal">', " "))
        note = "KIDScinema" if title.lower().startswith("kidscinema") else ""
        out.append(row("kask", datetime.date.fromisoformat(d.group(1)), t.group(1).zfill(5) if t else "", title, note, u.group(1)))
    return out


def parse_rio(h):
    out, url = [], SOURCES["rio"]
    blocks = re.findall(r"<h5>\s*PROGRAMMA\s*</h5>(.*?)(?:<h[1-5]|</div>)", h, re.S)
    for line in [l for b in blocks for l in re.split(r"<br\s*/?>|</p>", b)]:
        dm = re.search(r"\b(?:ma|di|wo|do|vr|za|zo)\s+(\d{1,2})\.(\d{1,2})\b", text(line))
        if not dm:
            continue
        d = year_for(int(dm.group(2)), int(dm.group(1)))
        em = re.search(r"<em>(.*?)(?:</em>|$)", line, re.S)
        note = text(em.group(1)) if em else ""
        rest = text(re.sub(r"<em>.*", "", line, flags=re.S))
        title = re.sub(r"^\S+\s+\d{1,2}\.\d{1,2}\s+", "", rest).strip()
        link = re.search(r'<a href="(https://dekoer\.be/programma/[^"]+)"', line)
        if d and title:
            out.append(row("rio", d, "", title, note, link.group(1) if link else url))
    # The page also has a dated list (year > month > day). Add events missing from the text lists above.
    have = {(r["d"], r["url"]) for r in out}
    y = mo = None
    for tok in re.finditer(r"<li>\s*(\d{4}|[a-z]+)\s*</li>|<a href=\"([^\"]+)\" class=\"d-block dk__programma\">(.*?)</a>", h, re.S):
        if tok.group(1):
            if tok.group(1).isdigit():
                y = int(tok.group(1))
            elif tok.group(1) in MONTHS:
                mo = MONTHS[tok.group(1)]
            continue
        dd = re.search(r'dk__programma__datum">(\d{1,2})<', tok.group(3))
        ti = re.search(r'dk__programma__titel"><span>(.*?)</span>', tok.group(3), re.S)
        if not (y and mo and dd and ti):
            continue
        try:
            d = datetime.date(y, mo, int(dd.group(1)))
        except ValueError:
            continue
        if (d.isoformat(), tok.group(2)) not in have:
            out.append(row("rio", d, "", text(ti.group(1)), "", tok.group(2)))
    return out


PARSERS = {"sphinx": parse_sphinx, "skoop": parse_skoop, "kask": parse_kask, "rio": parse_rio}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def main():
    dump = sys.argv[sys.argv.index("--dir") + 1] if "--dir" in sys.argv else None
    D = json.load(open("screenings.json", encoding="utf-8"))
    names = {k: D["venues"][k]["name"] for k in SOURCES}
    ok, failed = {}, []
    for v, url in SOURCES.items():
        try:
            h = open(f"{dump}/{v}.html", encoding="utf-8").read() if dump else fetch(url)
            rows = [r for r in PARSERS[v](h) if r["d"] >= TODAY.isoformat()]
            seen, uniq = set(), []
            for r in rows:
                key = (r["d"], r["t"], r["title"])
                if key not in seen:
                    seen.add(key); uniq.append(r)
            if not uniq:
                raise ValueError("no listings found (page layout may have changed)")
            ok[v] = uniq
        except Exception as e:  # keep last known data, report it
            failed.append(v)
            print(f"{v}: FAILED: {e}", file=sys.stderr)
    keep = [s for s in D["screenings"] if not (s["v"] in ok and s["d"] >= TODAY.isoformat())]
    for v in ok:
        keep.extend(ok[v])
    keep.sort(key=lambda s: (s["d"], s["t"] or "99", s["v"], s["title"]))
    D["screenings"] = keep
    D["notices"] = [n for n in D.get("notices", []) if not n.startswith(AUTO)]
    if failed:
        D["notices"].insert(0, f"{AUTO} on {TODAY.strftime('%d-%m-%Y')} the programme of {', '.join(names[v] for v in failed)} could not be read; showing the last known listings. Check the venue site.")
    D["updated"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    json.dump(D, open("screenings.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for v in SOURCES:
        print(f"{v}: {len(ok[v])} listings" if v in ok else f"{v}: kept last known listings")
    # A failing source is reported on the site, not as a failed run; fail only if everything broke.
    sys.exit(1 if len(failed) == len(SOURCES) else 0)


if __name__ == "__main__":
    main()
