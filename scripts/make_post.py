#!/usr/bin/env python3
"""Build today's Instagram carousel + caption from screenings.json.

Usage: python3 make_post.py [screenings.json] [YYYY-MM-DD] [outdir]
Rarity = how many times the film plays in Ghent from today on (all listed days).
Fewest screenings first; ties broken by fewer venues, then earliest start.
Uses only free software: Python 3 + Pillow + the open-source Inter font.
"""
import json, os, sys, datetime, zoneinfo, unicodedata
from PIL import Image, ImageDraw, ImageFont

SRC = sys.argv[1] if len(sys.argv) > 1 else "screenings.json"
TODAY = sys.argv[2] if len(sys.argv) > 2 else datetime.datetime.now(zoneinfo.ZoneInfo("Europe/Brussels")).strftime("%Y-%m-%d")
OUT = sys.argv[3] if len(sys.argv) > 3 else "post"
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT):
    if f.startswith("slide-") and f.endswith(".png"):
        os.remove(os.path.join(OUT, f))

D = json.load(open(SRC, encoding="utf-8"))
FILMS = {}
_fp = os.path.join(os.path.dirname(os.path.abspath(SRC)), "films.json")
if os.path.exists(_fp):
    for _f in json.load(open(_fp, encoding="utf-8"))["films"]:
        for _m in _f["match"]:
            FILMS[_m.lower()] = _f
V = D["venues"]

def key(t):
    if t.lower() in FILMS: return FILMS[t.lower()]["id"]
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return " ".join("".join(c if c.isalnum() else " " for c in t).split())

END = (datetime.date.fromisoformat(TODAY) + datetime.timedelta(days=6)).isoformat()
upcoming = [s for s in D["screenings"] if TODAY <= s["d"] <= END]  # rarity over a 7-day window
count = {}
for s in upcoming:
    count[key(s["title"])] = count.get(key(s["title"]), 0) + 1

films = {}
for s in [s for s in upcoming if s["d"] == TODAY]:
    meta = FILMS.get(s["title"].lower())
    f = films.setdefault(key(s["title"]), {"title": meta["title"] if meta else s["title"], "venues": {}, "notes": set(),
                                         "money": " · ".join(meta["studios"][:2]) if meta and meta["studios"] else ""})
    f["venues"].setdefault(s["v"], []).append(s["t"])
    if s.get("note"):
        f["notes"].add(s["note"])
for k, f in films.items():
    f["count"] = count[k]
    f["first"] = min((t for ts in f["venues"].values() for t in ts if t), default="99:99")
ranked = sorted(films.values(), key=lambda f: (f["count"], len(f["venues"]), f["first"], f["title"].lower()))

def tag(f):
    n = f["count"]
    if n == 1: return "ONLY SCREENING"
    if n <= 3: return f"RARE · {n}× THIS WEEK"
    return f"{n}× THIS WEEK"

def where(f):
    out = []
    for v, ts in f["venues"].items():
        ts = sorted(t for t in ts if t)
        out.append((v, V[v]["name"], " · ".join(ts) if ts else "time on venue site"))
    return out

day = datetime.date.fromisoformat(TODAY)
DAY = day.strftime("%A %-d %B")

# ---------- caption ----------
lines = [f"Ghent on screen · {DAY}", f"{len(ranked)} films at Ghent's arthouse cinemas and film clubs, rarest first.", ""]
for i, f in enumerate(ranked, 1):
    w = "; ".join(f"{n} {t}" for _, n, t in where(f))
    lines.append(f"{i}. {f['title']} — {w} ({tag(f).lower()})" + (f"\n   Money: {f['money']}" if f["money"] else ""))
lines += ["", "Sphinx · Studio Skoop · KASKcinema · Ciné Rio", "Times can change, check the venue before you go.", "",
          "#gent #ghent #filmgent #arthouse #cinema #filmclub #wattedoeningent"]
cap = "\n".join(lines)
if len(cap) > 2200:  # Instagram caption limit
    keep = lines[:3]
    for l in lines[3:3 + len(ranked)]:
        if len("\n".join(keep + [l])) > 1900: break
        keep.append(l)
    cap = "\n".join(keep + ["…full list in the slides", ""] + lines[-4:])
open(os.path.join(OUT, "caption.txt"), "w", encoding="utf-8").write(cap)

# ---------- slides ----------
W, H = 1080, 1350
BG, FG, MUTED, LINE, ACC, CARD = "#eef0f2", "#15181d", "#5d6570", "#d5d9de", "#9b1f35", "#ffffff"
VC = {"sphinx": "#2f5d8a", "skoop": "#9b1f35", "kask": "#3c7a52", "rio": "#8a5a14"}
FD = "/usr/share/fonts/opentype/inter/"
def F(name, size):
    try: return ImageFont.truetype(FD + name, size)
    except OSError: return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
BLACK, XB, BOLD, REG, SEMI = (lambda s: F("InterDisplay-Black.otf", s)), (lambda s: F("InterDisplay-ExtraBold.otf", s)), (lambda s: F("Inter-Bold.otf", s)), (lambda s: F("Inter-Regular.otf", s)), (lambda s: F("Inter-SemiBold.otf", s))

def wrap(d, text, font, width):
    words, rows, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= width: cur = t
        else: rows.append(cur); cur = w
    rows.append(cur)
    return rows

def footer(d, page, total):
    d.line([(72, H - 110), (W - 72, H - 110)], fill=LINE, width=2)
    d.text((72, H - 82), "GHENT SCREENS · Kinepolis not included", font=SEMI(26), fill=MUTED)
    d.text((W - 72, H - 82), f"{page}/{total}", font=SEMI(26), fill=MUTED, anchor="ra")

# measure film blocks, then paginate
probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
TF, TAGF, VF = XB(50), BOLD(24), REG(30)
blocks = []
for i, f in enumerate(ranked, 1):
    t = wrap(probe, f["title"], TF, W - 72 - 170)[:2]
    h = 22 + len(t) * 58 + 40 + len(f["venues"]) * 42 + (52 if f["money"] else 0) + 26
    blocks.append((i, f, t, h))
pages, cur, used, avail = [], [], 0, H - 150 - 140
for b in blocks:
    if cur and used + b[3] > avail: pages.append(cur); cur, used = [], 0
    cur.append(b); used += b[3]
if cur: pages.append(cur)
pages = pages[:9]  # cover + 9 = Instagram's classic 10-slide carousel
total = len(pages) + 1

# cover
im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
d.rectangle([0, 0, W, 18], fill=ACC)
d.text((72, 150), "GHENT", font=BLACK(190), fill=FG)
d.text((72, 340), "ON SCREEN", font=BLACK(150), fill=ACC)
d.text((72, 560), DAY.upper(), font=XB(64), fill=FG)
d.text((72, 650), f"{len(ranked)} films at arthouse cinemas and film clubs", font=REG(38), fill=MUTED)
d.text((72, 700), "Rarest first: swipe for times and venues", font=REG(38), fill=MUTED)
y = 830
for k, v in V.items():
    d.ellipse([72, y + 10, 96, y + 34], fill=VC.get(k, ACC))
    d.text((116, y), v["name"], font=BOLD(40), fill=FG)
    y += 66
footer(d, 1, total)
im.save(os.path.join(OUT, "slide-01.png"))

for p, page in enumerate(pages, 2):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 18], fill=ACC)
    d.text((72, 66), DAY.upper(), font=XB(40), fill=MUTED)
    y = 150
    for i, f, trows, h in page:
        d.rounded_rectangle([56, y, W - 56, y + h - 14], radius=14, fill=CARD)
        d.text((80, y + 18), f"{i:02d}", font=BLACK(64), fill=ACC if f["count"] <= 3 else LINE)
        tx, ty = 200, y + 22
        for r in trows:
            d.text((tx, ty), r, font=TF, fill=FG); ty += 58
        tg = tag(f)
        tw = d.textlength(tg, font=TAGF)
        hot = f["count"] <= 3
        d.rounded_rectangle([tx, ty + 4, tx + tw + 28, ty + 40], radius=18, fill=ACC if hot else BG)
        d.text((tx + 14, ty + 9), tg, font=TAGF, fill="#ffffff" if hot else MUTED)
        ty += 52
        for v, name, times in where(f):
            d.ellipse([tx, ty + 11, tx + 16, ty + 27], fill=VC.get(v, ACC))
            d.text((tx + 28, ty), f"{name}  ", font=BOLD(30), fill=FG)
            nx = tx + 28 + d.textlength(f"{name}  ", font=BOLD(30))
            d.text((nx, ty), times, font=VF, fill=MUTED)
            ty += 42
        if f["money"]:
            mt = "MONEY: " + f["money"]
            while d.textlength(mt, font=SEMI(26)) > W - 72 - tx - 24 and len(mt) > 10: mt = mt[:-2]
            if mt != "MONEY: " + f["money"]: mt = mt.rstrip() + "…"
            d.rounded_rectangle([tx - 2, ty + 2, tx + d.textlength(mt, font=SEMI(26)) + 16, ty + 36], radius=6, fill="#f4ecd3")
            d.text((tx + 7, ty + 5), mt, font=SEMI(26), fill="#6b5413")
            ty += 40
        y += h
    footer(d, p, total)
    im.save(os.path.join(OUT, f"slide-{p:02d}.png"))

json.dump({"date": TODAY, "slides": sorted(f for f in os.listdir(OUT) if f.startswith("slide-")),
           "caption": cap, "films": [{"rank": i, "title": f["title"], "count": f["count"], "tag": tag(f),
           "money": f["money"], "where": [{"venue": n, "times": t} for _, n, t in where(f)]} for i, f in enumerate(ranked, 1)]},
          open(os.path.join(OUT, "post.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{len(ranked)} films, {total} slides, caption {len(cap)} chars")
