#!/usr/bin/env python3
"""Weekly automatic update of theatre, dance and stage music (wave 2).

Venues: NTGent, VIERNULVIER, CAMPO, Kopergietery, Arca, Opera Ballet Vlaanderen (Ghent dates),
De Centrale, Theater Box and amateur theatre around Ghent (OPENDOEK calendar, 25 km around Gent).
Runs in GitHub Actions without Claude. Reads only official programme pages; keeps facts only
(date, time, title, short label, place, link): no images, no descriptions.
Robots.txt of every site allows these pages (checked 25-10-2026); VIERNULVIER and CAMPO ask for
5 s between requests, which is respected. A headless browser is used only for Arca and Opera Ballet,
whose calendars load with JavaScript.

Merge rule (same as wave 1): a venue that parses fine replaces its listings from today on;
a venue that fails keeps its last known listings and gets a notice on the site.

Usage: python3 scripts/update_stage.py
Python standard library + playwright (for two venues)."""
import datetime, html, http.cookiejar, json, re, sys, time, unicodedata, urllib.parse, urllib.request, zoneinfo

TZ = zoneinfo.ZoneInfo("Europe/Brussels")
TODAY = datetime.datetime.now(TZ).date()
UA = "GhentScreensBot/1.0 (+https://peapickers.github.io/ghent-screens/; weekly, programme facts only)"
AUTO = "Automatic update (stage):"
MONTHS = {m: i + 1 for i, m in enumerate("januari februari maart april mei juni juli augustus september oktober november december".split())}
MON3 = {"jan": 1, "feb": 2, "mrt": 3, "maa": 3, "apr": 4, "mei": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "okt": 10, "nov": 11, "dec": 12}
DELAY = {"www.viernulvier.gent": 5, "www.campo.nu": 5}
_last = {}
_jar = http.cookiejar.CookieJar()
_op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(_jar))
_op.addheaders = [("User-Agent", UA), ("Accept", "text/html,application/xhtml+xml")]


def fetch(url):
    host = urllib.parse.urlsplit(url).netloc
    wait = DELAY.get(host, 1.5) - (time.time() - _last.get(host, 0))
    if wait > 0:
        time.sleep(wait)
    try:
        with _op.open(url, timeout=40) as r:
            return r.read().decode("utf-8", "replace")
    finally:
        _last[host] = time.time()


def text(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z0-9]+", "", "".join(c for c in s if not unicodedata.combining(c)))


def near(month, day):
    for y in (TODAY.year - 1, TODAY.year, TODAY.year + 1):
        try:
            d = datetime.date(y, month, day)
        except ValueError:
            continue
        if TODAY - datetime.timedelta(days=7) <= d <= TODAY + datetime.timedelta(days=330):
            return d
    return None


def parse_day(s):
    """'wo 28.10', '28.10.26', 'do 29 okt', '13 november 2026', '11-11-2026' -> date."""
    s = s.lower()
    m = re.search(r"(\d{1,2})-(\d{1,2})-(\d{4})", s)
    if m:
        return datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    m = re.search(r"(\d{1,2})\.(\d{1,2})\.(\d{2,4})", s)
    if m:
        y = int(m.group(3)); y = y + 2000 if y < 100 else y
        return datetime.date(y, int(m.group(2)), int(m.group(1)))
    m = re.search(r"(\d{1,2})\.(\d{1,2})\b", s)
    if m:
        return near(int(m.group(2)), int(m.group(1)))
    m = re.search(r"(\d{1,2})\s+([a-z]+)\.?\s*(\d{4})?", s)
    if m:
        mon = MONTHS.get(m.group(2)) or MON3.get(m.group(2)[:3])
        if mon:
            return datetime.date(int(m.group(3)), mon, int(m.group(1))) if m.group(3) else near(mon, int(m.group(1)))
    return None


def hhmm(s):
    m = re.search(r"(\d{1,2})[:u.h](\d{2})", s or "")
    if m:
        return f"{int(m.group(1)):02d}:{m.group(2)}"
    m = re.search(r"\b(\d{1,2})u\b", s or "")
    return f"{int(m.group(1)):02d}:00" if m else ""


def row(v, d, t, title, k, url, note="", place="", city="Gent"):
    r = {"v": v, "d": d.isoformat(), "t": t, "title": text(title).replace("’", "'"), "note": text(note), "url": url, "k": k, "city": city or "Gent"}
    if place:
        r["place"] = text(place)
    return r


def split_location(loc):
    """'Arsenaalsite, Gent' -> ('Arsenaalsite', 'Gent'); 'De Vooruit, Gent' -> ('De Vooruit', 'Gent')."""
    loc = text(loc)
    if "," in loc:
        a, b = loc.rsplit(",", 1)
        b = re.sub(r"^\d{4}\s+", "", b.strip())
        return a.strip(), b.strip()
    return loc, "Gent"


# ---------------- CultureSuite sites: VIERNULVIER and CAMPO ----------------
GENRE_K = [("dans", "dance"), ("dance", "dance"), ("concert", "music"), ("nightlife", "music"), ("muziek", "music"),
           ("talks", "talk"), ("lezing", "talk"), ("debat", "talk"), ("film", "film"),
           ("muziektheater", "theatre"), ("opera", "theatre"), ("theater", "theatre"), ("performance", "theatre"),
           ("comedy", "theatre"), ("circus", "theatre")]
SKIP_GENRES = {"workshop", "installatie", "rondleiding", "gaming", "vr", "360° a/v", "op tournee", "community"}


def culturesuite(v, base, default_k):
    cards, seen, page = [], set(), 1
    while page <= 15:
        h = fetch(f"{base}/nl/agenda" + (f"?p54_page={page}" if page > 1 else ""))
        found = 0
        for c in re.split(r"<li\s+data-entry-id=", h)[1:]:
            m = re.search(r'href="(/nl/agenda/[a-z0-9-]+)"', c)
            if not m or m.group(1) in seen:
                continue
            seen.add(m.group(1)); found += 1
            genres = [text(g).lower() for g in re.findall(r'class="genres__link"[^>]*>(.*?)</a>', c, re.S)]
            cards.append({"path": m.group(1), "title": text((re.search(r'<h3 class="title">(.*?)</h3>', c, re.S) or [None, ""])[1]),
                          "sub": text((re.search(r'<div class="subtitle">(.*?)</div>', c, re.S) or [None, ""])[1]),
                          "genres": genres,
                          "venue": text((re.search(r'<div class="venue">(.*?)</div>', c, re.S) or [None, ""])[1]),
                          "date": text((re.search(r'<div class="top-date">(.*?)</div>', c, re.S) or [None, ""])[1]).replace(" -", " - "),
                          "time": text((re.search(r'<div class="time">(.*?)</div>', c, re.S) or [None, ""])[1])})
        if not found or f"p54_page={page + 1}" not in h:
            break
        page += 1
    out = []
    for c in cards:
        if any(g in SKIP_GENRES for g in c["genres"]):
            continue
        k = next((kk for g in c["genres"] for key, kk in GENRE_K if key == g or g.startswith(key)), default_k)
        if not k:
            continue
        url = base + c["path"]
        try:
            h = fetch(url)
        except Exception:
            h = ""
        subs = re.split(r'<li class="subshow', h)[1:]
        if not subs and c["date"] and " - " not in c["date"]:
            d = parse_day(c["date"])
            if d:
                out.append(row(v, d, hhmm(c["time"]), c["title"], k, url, c["sub"], c["venue"], "Gent"))
        for s in subs:
            if "geannuleerd" in s[:3000] and "status-geannuleerd" in s:
                continue
            ds = re.search(r'<div class="date">\s*<div class="start">(.*?)</div>', s, re.S)
            ts = re.search(r'<div class="time">\s*<span class="start">(.*?)</span>', s, re.S)
            loc = re.search(r'<div class="location">(.*?)</div>', s, re.S)
            ven = re.search(r'<div class="venue">(.*?)</div>', s, re.S)
            d = parse_day(text(ds.group(1))) if ds else None
            if not d:
                continue
            place, city = split_location(loc.group(1)) if loc else ("", "Gent")
            room = text(ven.group(1)) if ven else ""
            place = " · ".join(x for x in (place, room) if x)
            sold = "sold out" if "uitverkocht" in s[:4000].lower() else ""
            out.append(row(v, d, hhmm(text(ts.group(1))) if ts else "", c["title"], k, url,
                           ", ".join(x for x in (c["sub"], sold) if x), place, city))
    return out


# ---------------- NTGent ----------------
def ntgent():
    h = fetch("https://www.ntgent.be/nl/programma")
    slugs = list(dict.fromkeys(re.findall(r'href="/nl/producties/([^"#?]+)"', h)))
    out = []
    for slug in slugs:
        url = "https://www.ntgent.be/nl/producties/" + slug
        try:
            p = fetch(url)
        except Exception:
            continue
        items = []
        for m in re.finditer(r'self\.__next_f\.push\(\[1,("(?:[^"\\]|\\.)*")\]\)', p):
            try:
                chunk = json.loads(m.group(1))
            except Exception:
                continue
            j = chunk.find('"eventItems":[')
            if j >= 0:
                try:
                    items, _ = json.JSONDecoder().raw_decode(chunk, j + len('"eventItems":'))
                except Exception:
                    items = []
                break
        for e in items:
            sd = e.get("startDate", "")
            loc = " ".join(l.get("title", "") for l in e.get("location") or [])
            it = (e.get("item") or [{}])[0]
            if not re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", sd):
                continue
            if loc and not re.search(r"ntgent|schouwburg|minnemeers|kns|gent|campo|vooruit|viernulvier|arca|bijloke", loc, re.I):
                continue  # touring date outside Ghent
            out.append(row("ntgent", datetime.date.fromisoformat(sd[:10]), sd[11:16], it.get("title") or slug, "theatre", url,
                           it.get("author", ""), loc))
    return out


# ---------------- Kopergietery ----------------
def kopergietery():
    h = fetch("https://kopergietery.be/programma")
    sec = h.split('<h2 class="red bb section-title">', 2)
    gent = sec[1] if len(sec) > 1 else h
    links = list(dict.fromkeys(re.findall(r'href="(https://kopergietery\.be/programma/[a-z0-9-]+)"', gent)))
    out = []
    for url in links:
        p = fetch(url)
        title = text((re.search(r"<h1[^>]*>(.*?)</h1>", p, re.S) or re.search(r"<title>KOPERGIETERY \| (.*?)</title>", p, re.S) or [None, ""])[1])
        i = p.find("Speeldata in Gent")
        if i < 0:
            continue
        stop = min([x for x in (p.find("Speeldata op reis", i), p.find("Voorbije speeldata", i)) if x > 0] or [len(p)])
        for blk in re.split(r'<div class="playdate', p[i:stop])[1:]:
            dm = re.search(r'<div class="date">(.*?)</div>', blk, re.S)
            lm = re.search(r'<div class="location"><span>(.*?)</span>', blk, re.S)
            d = parse_day(text(dm.group(1))) if dm else None
            if d:
                place, city = split_location(lm.group(1)) if lm else ("", "Gent")
                sold = "sold out" if re.search(r'class="status">\s*uitverkocht', blk) else ""
                out.append(row("kopergietery", d, hhmm(text(dm.group(1)).split("—")[-1]), title, "theatre", url, sold, place, city))
    return out


# ---------------- De Centrale ----------------
def decentrale():
    h = fetch("https://www.decentrale.be/nl/agenda")
    out = []
    for a in re.findall(r"<article[^>]*>(.*?)</article>", h, re.S):
        u = re.search(r'href="(https://www\.decentrale\.be/nl/agenda/([a-z-]+)/[^"]+)"', a)
        n = re.search(r'itemprop="name">(.*?)</h1>', a, re.S)
        d = re.search(r'datetime="(\d{4}-\d{2}-\d{2})"', a)
        if not (u and n and d):
            continue
        title, cat = text(n.group(1)), u.group(2)
        k = "dance" if re.search(r"dans|dance|battle|freestyle", title, re.I) else ("theatre" if cat == "theater-film" else "music")
        out.append(row("decentrale", datetime.date.fromisoformat(d.group(1)), "", title, k, u.group(1)))
    return out


# ---------------- Theater Box ----------------
def box():
    h = fetch("https://theaterbox.be/kalender.html")
    out, year, month = [], None, None
    for m in re.finditer(r'<span style="font-weight: bold;">([a-z]+) (20\d\d)</span>|<a class="link2" href="([^"]+)"[^>]*>(.*?)</a>', h):
        if m.group(1):
            month, year = MONTHS.get(m.group(1)), int(m.group(2)); continue
        if not year:
            continue
        line = text(m.group(4))
        lm = re.match(r"\w+dag\s+(\d{1,2})\s+([a-z]+),\s*([\d.:u]+)\s*:\s*(.+)$", line)
        if not lm:
            continue
        mon = MONTHS.get(lm.group(2), month)
        try:
            d = datetime.date(year + (1 if mon < month else 0), mon, int(lm.group(1)))
        except (ValueError, TypeError):
            continue
        title, _, company = lm.group(4).rpartition(" - ")
        out.append(row("box", d, hhmm(lm.group(3)), title or lm.group(4), "theatre", m.group(3), company if title else ""))
    return out


# ---------------- OPENDOEK (amateur theatre, 25 km around Gent) ----------------
def opendoek():
    h = fetch("https://www.opendoek.be/beleven/kalender?city=Gent&radius=25")
    links = list(dict.fromkeys(re.findall(r'href="(https://www\.opendoek\.be/beleven/kalender/[a-z0-9-]+)"', h)))
    out = []
    for url in links:
        p = fetch(url)
        t = text(re.sub(r"<(script|style)[^>]*>.*?</\1>", "", p, flags=re.S))
        title = text((re.search(r"<h1[^>]*>(.*?)</h1>", p, re.S) or [None, ""])[1])
        w2 = t.find(" Wanneer ")
        w1 = t.rfind(" Waar ", 0, w2) if w2 > 0 else -1
        place, city = "", "Gent"
        if w1 >= 0:
            parts = [x.strip() for x in t[w1 + 6:w2].split(",")]
            place = parts[0]
            cm = re.search(r"\d{4}\s+(.+)$", parts[-1])
            city = cm.group(1) if cm else city
        comp = text((re.search(r"</h1>\s*(?:<[^>]+>\s*)*([^<]{3,80})<", p, re.S) or [None, ""])[1])
        sp = t.find("Speeldata")
        for m in re.finditer(r"(\d{1,2}) ([a-z]+) (20\d\d) (\d{1,2}:\d{2})", t[sp:sp + 3000] if sp >= 0 else ""):
            mon = MONTHS.get(m.group(2))
            if mon:
                out.append(row("opendoek", datetime.date(int(m.group(3)), mon, int(m.group(1))), hhmm(m.group(4)), title, "theatre", url, comp, place, city))
    return out


# ---------------- Rendered calendars: Arca and Opera Ballet Vlaanderen ----------------
def rendered(pages):
    from playwright.sync_api import sync_playwright
    res = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for key, url, more in pages:
            pg = b.new_page(user_agent=UA)
            pg.goto(url, wait_until="networkidle", timeout=60000)
            for sel in ("button.cmplz-deny", "#CybotCookiebotDialogBodyButtonDecline", "text=Weigeren"):
                try:
                    if pg.locator(sel).count():
                        pg.locator(sel).first.click(timeout=3000); break
                except Exception:
                    pass
            last = -1
            for _ in range(25):
                if more:
                    try:
                        pg.get_by_text(more).first.click(timeout=4000, force=True); pg.wait_for_timeout(2000)
                    except Exception:
                        pass
                pg.mouse.wheel(0, 8000); pg.wait_for_timeout(900)
                n = len(pg.content())
                if n == last:
                    break
                last = n
            res[key] = pg.content(); pg.close()
        b.close()
    return res


def arca(h):
    out = []
    for blk in re.split(r'class="wpem-event-layout-wrapper', h)[1:]:
        u = re.search(r'href="(https://www\.arcatheater\.be/[^"]+)"', blk)
        ti = re.search(r'class="wpem-event-title[^"]*"[^>]*>(.*?)</', blk, re.S)
        dm = re.search(r"(\d{2}-\d{2}-\d{4})\s*/\s*(\d{1,2}:\d{2})", text(blk))
        if not (u and ti and dm):
            continue
        ty = text((re.search(r'class="wpem-event-type-text[^"]*"[^>]*>(.*?)</', blk, re.S) or [None, ""])[1]).lower()
        k = "talk" if "debat" in ty else ("music" if "concert" in ty or "muziek" in ty and "theater" not in ty else "theatre")
        if "workshop" in ty:
            continue
        out.append(row("arca", parse_day(dm.group(1)), hhmm(dm.group(2)), text(ti.group(1)), k, u.group(1)))
    return out


GENT_HALLS = re.compile(r"gent|bijloke|ntgent|vooruit|viernulvier|miry|minard|capitole|kopergietery|campo|arca|schouwburg", re.I)


def opera(pages):
    kinds = {}
    for key, k in (("opera_dans", "dance"), ("opera_opera", "theatre"), ("opera_conc", "theatre"), ("opera_vonk", "theatre")):
        for li in re.findall(r'<li class="c-event">(.*?)</li>', pages.get(key, ""), re.S):
            hm = re.search(r'href="(/nl/programma/[^"]+)"', li)
            if hm:
                kinds[hm.group(1)] = k
    out = []
    for li in re.findall(r'<li class="c-event">(.*?)</li>', pages.get("opera_all", ""), re.S):
        dm = re.search(r"<time[^>]*>(.*?)</time>", li, re.S)
        hm = re.search(r'href="(/nl/programma/[^"]+)"', li)
        ti = re.search(r"<h3[^>]*>(.*?)</h3>", li, re.S)
        pm = re.search(r"<h3[^>]*>.*?</h3>\s*<p[^>]*>(.*?)</p>", li, re.S)
        if not (dm and hm and ti and pm):
            continue
        info = text(pm.group(1))
        hall = re.sub(r"^\s*\d{1,2}[:.]\d{2}u?\s*-\s*\d{1,2}[:.]\d{2}u?\s*", "", info)
        if not GENT_HALLS.search(hall) or re.search(r"antwerpen", hall, re.I):
            continue
        d = parse_day(text(dm.group(1)))
        if d:
            out.append(row("opera", d, hhmm(info), text(ti.group(1)), kinds.get(hm.group(1), "music"),
                           "https://www.operaballet.be" + urllib.parse.quote(hm.group(1)), "Opera Ballet Vlaanderen", hall))
    return out


NEW_VENUES = {
    "campo": {"name": "CAMPO", "addr": "Nieuwpoort 31-35 & Fratersplein 7, 9000 Gent", "url": "https://www.campo.nu/nl/agenda", "kind": "arts centre (theatre, dance, performance)"},
    "arca": {"name": "Arca Theater", "addr": "Sint-Widostraat 4, 9000 Gent", "url": "https://www.arcatheater.be/agenda/", "kind": "theatre"},
    "opera": {"name": "Opera Ballet Vlaanderen", "addr": "Ghent dates only (various halls)", "url": "https://www.operaballet.be/nl/kalender", "kind": "opera, ballet & concerts"},
    "decentrale": {"name": "De Centrale", "addr": "Kraankindersstraat 2, 9000 Gent", "url": "https://www.decentrale.be/nl/agenda", "kind": "intercultural music centre"},
    "opendoek": {"name": "Amateur theatre (OPENDOEK)", "addr": "various, within 25 km of Gent", "url": "https://www.opendoek.be/beleven/kalender", "kind": "amateur theatre companies"},
}
# Order = priority when the same performance is listed by two houses (kept once, at the first).
SOURCES = ["ntgent", "campo", "viernulvier", "kopergietery", "arca", "opera", "decentrale", "box", "opendoek"]


def main():
    D = json.load(open("screenings.json", encoding="utf-8"))
    for k, v in NEW_VENUES.items():
        D["venues"].setdefault(k, v)
    names = {k: D["venues"][k]["name"] for k in SOURCES}
    jobs = {
        "ntgent": ntgent,
        "campo": lambda: culturesuite("campo", "https://www.campo.nu", "theatre"),
        "viernulvier": lambda: culturesuite("viernulvier", "https://www.viernulvier.gent", None),
        "kopergietery": kopergietery, "decentrale": decentrale, "box": box, "opendoek": opendoek,
    }
    ok, failed = {}, []
    for v in SOURCES:
        if v not in jobs:
            continue
        try:
            ok[v] = jobs[v]()
        except Exception as e:
            print(f"{v}: FAILED: {e}", file=sys.stderr); failed.append(v)
    try:
        pages = rendered([
            ("arca", "https://www.arcatheater.be/agenda/", "Laad meer evenementen"),
            ("opera_all", "https://www.operaballet.be/nl/kalender", None),
            ("opera_dans", "https://www.operaballet.be/nl/kalender?types=dans", None),
            ("opera_opera", "https://www.operaballet.be/nl/kalender?types=Opera", None),
            ("opera_conc", "https://www.operaballet.be/nl/kalender?types=concertante%20opera", None),
            ("opera_vonk", "https://www.operaballet.be/nl/kalender?types=vonk", None),
        ])
        ok["arca"] = arca(pages.get("arca", ""))
        ok["opera"] = opera(pages)
    except Exception as e:
        print(f"browser: FAILED: {e}", file=sys.stderr); failed += ["arca", "opera"]
    # drop past dates, empty results and duplicates (within and across houses)
    taken = {}
    for v in SOURCES:
        if v not in ok:
            continue
        uniq = []
        for r in ok[v]:
            n, slot = norm(r["title"]), taken.setdefault((r["d"], r["t"]), [])
            dup = any(n == x or (min(len(n), len(x)) >= 6 and (n.startswith(x) or x.startswith(n))) for x in slot)
            if r["d"] < TODAY.isoformat() or dup:
                continue
            slot.append(n); uniq.append(r)
        if uniq:
            ok[v] = uniq
        else:
            del ok[v]; failed.append(v); print(f"{v}: FAILED: no listings found", file=sys.stderr)
    keep = [s for s in D["screenings"] if not (s["v"] in ok and s["d"] >= TODAY.isoformat())]
    for v in ok:
        keep.extend(ok[v])
    keep.sort(key=lambda s: (s["d"], s["t"] or "99", s["v"], s["title"]))
    D["screenings"] = keep
    D["notices"] = [n for n in D.get("notices", []) if not n.startswith(AUTO)]
    if failed:
        D["notices"].insert(0, f"{AUTO} on {TODAY.strftime('%d-%m-%Y')} the programme of {', '.join(names[v] for v in dict.fromkeys(failed))} could not be read; showing the last known listings. Check the venue site.")
    D["updated"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    json.dump(D, open("screenings.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for v in SOURCES:
        print(f"{v}: {len(ok[v])} listings" if v in ok else f"{v}: kept last known listings")
    sys.exit(1 if len(ok) == 0 else 0)


if __name__ == "__main__":
    main()
