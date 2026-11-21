"""Draw "The World Today - 20 November 2026", a one-page newspaper poster.

Pure stdlib (zlib, struct, math, os, sys). Renders from embedded 1-bit
bitmap glyphs (fontdata.py, DejaVu family) onto an RGB canvas and writes a
deterministic PNG. No network, no third-party packages.

Layout (1024 x 1024):
  masthead (navy) | verification strip | 3 hero panels | numbered grid
  (20 stories) | dotted world map with numbered pins | ALSO ON (13 more)
  | markets ticker | footer with sources + UTC timeline.
36 stories in all, 7 regions, lead: Kyiv barrage + Cyclone Akvan + AI sell-off.
"""

import math
import os
import struct
import sys
import zlib

import fontdata

W, H = 1024, 1024

# ---- palette ----
PAPER = (247, 243, 234)
INK = (17, 17, 17)
NAVY = (13, 27, 46)
NAVY2 = (20, 42, 68)
RED = (179, 38, 30)
RED_DK = (140, 28, 22)
BLUE = (29, 78, 137)
TEAL = (14, 124, 123)
GOLD = (200, 150, 60)
GREY = (107, 107, 107)
LINE = (216, 210, 196)
LIGHT = (238, 233, 221)
WHITE = (255, 255, 255)
SKY = (38, 58, 86)
ORANGE = (232, 120, 40)

# ---- canvas ----
_buf = bytearray(W * H * 3)


def _set(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        _buf[i], _buf[i + 1], _buf[i + 2] = c


def rect(x, y, w, h, c):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            _buf[i], _buf[i + 1], _buf[i + 2] = c


def hline(x, y, w, c):
    rect(x, y, w, 1, c)


def vline(x, y, h, c):
    rect(x, y, 1, h, c)


def line(x0, y0, x1, y1, c):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        _set(x0, y0, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def circle(cx, cy, r, c, fill=False):
    if fill:
        for yy in range(cy - r, cy + r + 1):
            half = int(math.sqrt(max(0, r * r - (yy - cy) ** 2)))
            for xx in range(cx - half, cx + half + 1):
                _set(xx, yy, c)
    else:
        x, y, d = r, 0, 1 - r
        while x >= y:
            for px, py in ((cx + x, cy + y), (cx + y, cy + x), (cx - y, cy + x),
                           (cx - x, cy + y), (cx - x, cy - y), (cx - y, cy - x),
                           (cx + y, cy - x), (cx + x, cy - y)):
                _set(px, py, c)
            y += 1
            if d <= 0:
                d += 2 * y + 1
            else:
                x -= 1
                d += 2 * (y - x) + 1


def poly(points, c):
    """Scanline-fill a polygon given as [(x, y), ...]."""
    if len(points) < 3:
        return
    ys = [p[1] for p in points]
    for y in range(max(0, min(ys)), min(H, max(ys) + 1)):
        xs = []
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            for x in range(int(xs[i]), int(xs[i + 1]) + 1):
                _set(x, y, c)


def starburst(cx, cy, r, c):
    for k in range(12):
        a = k * math.pi / 6
        line(cx, cy, int(cx + r * math.cos(a)), int(cy + r * math.sin(a)), c)
    circle(cx, cy, max(2, r // 3), c, fill=True)


# ---- fonts ----
_FONTS = {}


def font(name):
    if name not in _FONTS:
        _FONTS[name] = fontdata.load(name)
    return _FONTS[name]


def text_w(s, fname):
    g = font(fname)
    return sum(g.get(ch, (0, 0, 0, 0, 0, b""))[0] for ch in s)


def draw_text(x, y, s, fname, c):
    """Draw text with (x, y) at the ascender line. Returns width used."""
    g = font(fname)
    px = x
    for ch in s:
        adv, dx, dy, w, h, bits = g.get(ch, (0, 0, 0, 0, 0, b""))
        if w and h:
            bit = 0
            for yy in range(h):
                for xx in range(w):
                    if bits[bit // 8] >> (7 - bit % 8) & 1:
                        _set(px + dx + xx, y + dy + yy, c)
                    bit += 1
        px += adv
    return px - x


def text_h(fname):
    """Approx line height for a variant from its size suffix."""
    return int(fname.rsplit("_", 1)[1]) + 4


def wrap(s, fname, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    g = font(fname)
    words = s.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(trial, fname) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(x, y, s, fname, c, max_w, leading=None):
    lh = leading if leading is not None else text_h(fname)
    for ln in wrap(s, fname, max_w):
        draw_text(x, y, ln, fname, c)
        y += lh
    return y


def center_text(cx, y, s, fname, c):
    draw_text(cx - text_w(s, fname) // 2, y, s, fname, c)


# ---- PNG writer (deterministic: fixed compression, no metadata) ----
def write_png(path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += _buf[y * W * 3:(y + 1) * W * 3]
    comp = zlib.compress(bytes(raw), 6)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ---- stories: 36 in all, verified against wire reporting of 20 Nov 2026 ----
HEROES = [
    {
        "num": 1, "tag": "EUROPE  |  UKRAINE", "art": "kyiv",
        "color": RED,
        "title": "KYIV BRIDGES HIT IN MASS BARRAGE",
        "body": "Russia fires 400+ drones and 110 missiles; 3 Dnipro bridges hit, 8 killed.",
        "fig": "400+ DRONES - 110 MISSILES - 8 KILLED",
    },
    {
        "num": 2, "tag": "ASIA  |  INDIA", "art": "akvan",
        "color": TEAL,
        "title": "CYCLONE AKVAN SLAMS ODISHA COAST",
        "body": "Severe storm crosses near Gopalpur at 70-80 km/h; heavy rain spreads over Bengal.",
        "fig": "70-80 KM/H - GUSTS 90 - 08:30 IST",
    },
    {
        "num": 3, "tag": "MARKETS  |  GLOBAL", "art": "markets",
        "color": NAVY2,
        "title": "AI SELL-OFF DRAGS S&P INTO CORRECTION",
        "body": "S&P 500 -3.7% for a seventh straight loss; Nasdaq -5.28% erases 2026 gains.",
        "fig": "S&P -3.70% - NASDAQ -5.28% - NIKKEI -5.06%",
    },
]

# (number, region, headline, summary) -- summaries kept short so each fits 2 lines
GRID = [
    (4, "EUROPE", "Russian missiles land in Poland",
     "Two missiles land in the east; NATO calls it a grave violation."),
    (5, "JUSTICE", "World court: Myanmar committed genocide",
     "First time a state is held responsible; refugees to return."),
    (6, "DIPLOMACY", "Trump, Xi and Putin end summit with little",
     "Joint declaration on nuclear war and oil; little else of substance."),
    (7, "MIDDLE EAST", "Houthis fire missiles at Riyadh",
     "Coalition intercepts three missiles; hits Hodeidah as 41 are killed."),
    (8, "EUROPE", "UK and EU sign food and carbon deals",
     "Food trade, linked carbon markets and youth mobility agreed."),
    (9, "CONFLICT", "Kerch Bridge hit for a third time",
     "Third strike in four days halts rail; Putin vows a painful response."),
    (10, "TECH", "Anthropic debuts 17% above IPO price",
     "Shares close near $97 after a record $81.3B raise."),
    (11, "CLIMATE", "COP31 runs into overtime",
     "Draft omits fossil-fuel phase-out; EU warns of a 'fossil summit'."),
    (12, "SPACE", "BepiColombo reaches Mercury orbit",
     "Twin probes enter orbit after an eight-year, 10-billion-km journey."),
    (13, "DISASTER", "Magnitude 6.7 quake hits central Peru",
     "Tremor near Cerro de Pasco shakes Lima; buildings evacuated."),
    (14, "CONFLICT", "Israeli forces cross Yellow Line",
     "First incursion since the truce; six killed in strikes."),
    (15, "CONFLICT", "Iran war nears its ninth month",
     "Trump in no rush on decisions; a tanker burns near Hormuz."),
    (16, "TECH", "Nvidia under more pressure",
     "Chip-export records released; SEC examines the firm's accounting."),
    (17, "JUSTICE", "Palisades Fire arson verdict",
     "Rinderknecht convicted; the fire killed 12 and burned 23,000 acres."),
    (18, "TECH", "Trump threatens tax on AI data centers",
     "Firms building AI centers abroad face a 'tremendous tax', he says."),
    (19, "DIPLOMACY", "Ukraine allies meet in Berlin",
     "Europe is ready to talk with Russia, the coalition says."),
    (20, "SCIENCE", "Pill hailed for pancreatic cancer",
     "Trial of daraxonrasib stops tumors growing in nearly all patients."),
    (21, "EUROPE", "Denmark expels Russian diplomat",
     "Two arrested over an alleged plot to kill rapper Kyivstoner."),
    (22, "EUROPE", "Estonia to shut Russia border crossings",
     "Five checkpoints close from Dec 1 after a blamed sabotage attack."),
    (23, "EUROPE", "Students march in 25 countries",
     "Tens of thousands protest living costs, tuition and rearmament."),
]

# (number, one-line story)
ALSO_ON = [
    (24, "Texas execution lasting an hour draws scrutiny"),
    (25, "Bayer's $7.25B Roundup settlement approved"),
    (26, "Iraqi forces enter Jurf al-Nasr after 12 years"),
    (27, "Nigeria boat capsizes; 4 dead, 300 feared missing"),
    (28, "Bangladesh unrest ahead of Hasina's return"),
    (29, "Indian man gets 19 years in Sikh murder plot"),
    (30, "Fiji and Tonga declare disasters as drought worsens"),
    (31, "Migrant boat capsizes off Senegal"),
    (32, "Sudan drone strike kills 10 at gold mine"),
    (33, "US Senate passes energy permitting bill 62-33"),
    (34, "Brazil's central bank sells $1B to curb dollar"),
    (35, "US and Venezuela sign military deal"),
    (36, "GTA 6 sets $3.8B launch-day record"),
]

# ---- dotted world map: land mask, 96 cols x 30 rows, lon -180..180, lat 72..-44 ----
# Rows are built from (start, end) column ranges so the shapes stay exact.
_MAP_ROWS = [
    [(6, 11), (13, 28), (33, 36), (56, 92)],
    [(6, 12), (12, 29), (32, 37), (46, 48), (52, 93)],
    [(7, 13), (12, 28), (39, 40), (46, 53), (54, 92)],
    [(8, 14), (13, 28), (35, 36), (43, 44), (47, 50), (55, 91)],
    [(14, 27), (43, 45), (47, 49), (50, 52), (53, 90)],
    [(15, 26), (43, 44), (46, 52), (53, 89)],
    [(16, 27), (45, 53), (54, 58), (60, 86), (89, 90)],
    [(17, 28), (45, 56), (58, 63), (64, 84), (88, 89)],
    [(18, 29), (44, 53), (54, 58), (62, 82), (87, 88)],
    [(19, 30), (44, 45), (47, 52), (54, 57), (59, 62), (66, 70), (73, 82)],
    [(20, 29), (46, 59), (60, 62), (66, 70), (74, 81)],
    [(21, 26), (47, 58), (60, 63), (67, 70), (73, 76), (77, 81)],
    [(22, 26), (48, 58), (60, 62), (67, 69), (74, 77)],
    [(23, 26), (49, 57), (68, 69), (75, 78)],
    [(24, 27), (50, 57), (68, 68), (75, 79)],
    [(25, 28), (51, 57), (76, 79)],
    [(29, 32), (52, 56), (77, 79)],
    [(29, 33), (52, 56), (78, 82)],
    [(30, 34), (53, 55), (79, 84)],
    [(30, 34), (53, 55), (80, 85), (87, 89)],
    [(31, 34), (53, 55), (81, 85), (87, 89)],
    [(31, 34), (54, 55), (82, 88)],
    [(31, 33), (54, 54), (56, 56), (82, 89)],
    [(31, 33), (53, 54), (56, 56), (82, 88)],
    [(31, 33), (53, 54), (83, 88)],
    [(32, 33), (53, 53), (83, 87)],
    [(32, 33), (52, 53), (84, 87), (91, 92)],
    [(32, 33), (52, 52), (85, 87), (92, 92)],
    [(32, 32), (92, 92)],
    [(32, 32)],
]
MAP_COLS = 96
MAP_ROWS_N = 30
MAP_LAT_TOP = 72.0
MAP_LAT_BOT = -44.0

# (story number, lon, lat) pins on the map
PINS = [
    (1, 30.52, 50.45), (2, 84.92, 19.27), (3, -74.0, 40.71),
    (4, 22.57, 51.25), (5, 4.31, 52.08), (6, 114.06, 22.55),
    (7, 46.68, 24.71), (8, 4.35, 50.85), (9, 36.47, 45.36),
    (13, -76.26, -10.67), (14, 34.47, 31.50), (30, 178.44, -17.73),
]


# ---- hero illustrations (geometric, drawn, no photos) ----
def art_kyiv(x, y, w, h):
    rect(x, y, w, h, SKY)
    # river band at the bottom
    rect(x, y + h - 22, w, 22, (24, 60, 96))
    # three bridge arches over the river
    for i, bx in enumerate((x + 18, x + w // 2 - 30, x + w - 78)):
        bw = 60
        by = y + h - 22
        for t in range(0, 31):
            a = math.pi * t / 30
            px = int(bx + bw * t / 30)
            py = int(by - 26 * math.sin(a))
            _set(px, py, WHITE)
            _set(px, py + 1, WHITE)
        vline(bx, by - 26, 26, WHITE)
        vline(bx + bw, by - 26, 26, WHITE)
    # missile trails (diagonal, bright heads)
    for (sx, sy, ex, ey) in ((x + 30, y + 8, x + 90, y + 52),
                             (x + 150, y + 4, x + 210, y + 48),
                             (x + 250, y + 10, x + 290, y + 44)):
        line(sx, sy, ex, ey, (255, 210, 120))
        circle(ex, ey, 3, (255, 240, 180), fill=True)
    # explosion bursts on two bridges
    starburst(x + 48, y + h - 40, 12, ORANGE)
    starburst(x + 48, y + h - 40, 6, (255, 220, 120))
    starburst(x + w - 48, y + h - 44, 10, ORANGE)
    starburst(x + w - 48, y + h - 44, 5, (255, 220, 120))


def art_akvan(x, y, w, h):
    rect(x, y, w, h, (16, 74, 96))
    # coastline at the bottom
    poly([(x, y + h), (x, y + h - 26), (x + 90, y + h - 34),
          (x + 180, y + h - 24), (x + w, y + h - 30), (x + w, y + h)],
         (38, 110, 70))
    # cyclone spiral (Archimedean), centred above the coast
    cx, cy = x + w // 2, y + h // 2 - 4
    pts = []
    for k in range(0, 150):
        t = k * math.pi / 45
        r = 2 + 0.13 * k
        pts.append((int(cx + r * math.cos(t)), int(cy + r * math.sin(t))))
    for i in range(len(pts) - 1):
        line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], WHITE)
    circle(cx, cy, 4, (255, 220, 120), fill=True)
    # rain streaks
    for rx in range(x + 12, x + w - 8, 22):
        line(rx, y + 5, rx - 5, y + 15, (180, 215, 235))
        line(rx + 8, y + 22, rx + 3, y + 32, (180, 215, 235))


def art_markets(x, y, w, h):
    rect(x, y, w, h, (18, 26, 38))
    # descending bars, scaled to the art height
    fracs = [1.0, 0.9, 0.93, 0.77, 0.65, 0.48, 0.29]
    max_bh = h - 16
    bw = w // 9
    for i, f in enumerate(fracs):
        bh = int(max_bh * f)
        bx = x + 14 + i * bw
        rect(bx, y + h - 10 - bh, bw - 6, bh, RED)
    # falling jagged line over the bars
    fx = [0.05, 0.17, 0.29, 0.41, 0.53, 0.65, 0.77, 0.89, 0.96]
    fy = [0.28, 0.44, 0.38, 0.62, 0.55, 0.78, 0.72, 0.92, 0.88]
    pts = [(x + int(f * w), y + int(g * h)) for f, g in zip(fx, fy)]
    for i in range(len(pts) - 1):
        line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], WHITE)
        circle(pts[i][0], pts[i][1], 2, WHITE, fill=True)
    circle(pts[-1][0], pts[-1][1], 3, ORANGE, fill=True)


ARTS = {"kyiv": art_kyiv, "akvan": art_akvan, "markets": art_markets}


# ---- layout ----
MX = 24          # side margin
CW = W - 2 * MX  # content width


def masthead():
    rect(0, 0, W, 116, NAVY)
    rect(0, 112, W, 4, GOLD)
    center_text(W // 2, 30, "THE WORLD TODAY", "serif_bold_40", WHITE)
    center_text(W // 2, 84, "FRIDAY,  20 NOVEMBER 2026", "sans_bold_14", (255, 220, 140))
    center_text(W // 2, 98, "36 STORIES  -  7 REGIONS  -  EVERY FIGURE ATTRIBUTED",
                "sans_bold_12", (190, 205, 225))


def verify_strip():
    rect(0, 116, W, 24, LIGHT)
    hline(0, 139, W, (200, 192, 172))
    center_text(W // 2, 124,
                "DATE-CHECKED 20 NOV 2026  |  SOURCES: BBC - REUTERS - AP - AL JAZEERA - THE GUARDIAN - PBS",
                "sans_10", GREY)


def heroes():
    y0, hh = 140, 196
    gap = 8
    pw = (CW - 2 * gap) // 3
    art_h = 58
    paper_top = y0 + 22 + art_h
    for i, hero in enumerate(HEROES):
        x = MX + i * (pw + gap)
        # number tab + tag band
        rect(x, y0, pw, 22, hero["color"])
        draw_text(x + 8, y0 + 5, str(hero["num"]), "sans_bold_14", WHITE)
        draw_text(x + 26, y0 + 6, hero["tag"], "sans_bold_11", WHITE)
        # illustration
        ARTS[hero["art"]](x, y0 + 22, pw, art_h)
        # headline + body on paper
        rect(x, paper_top, pw, y0 + hh - paper_top, PAPER)
        ty = paper_top + 10
        for ln in wrap(hero["title"], "sans_bold_22", pw - 16)[:2]:
            draw_text(x + 8, ty, ln, "sans_bold_22", INK)
            ty += 24
        ty += 2
        for ln in wrap(hero["body"], "sans_13", pw - 16)[:2]:
            draw_text(x + 8, ty, ln, "sans_13", INK)
            ty += 16
        # figure line
        hline(x + 8, y0 + hh - 20, pw - 16, LINE)
        draw_text(x + 8, y0 + hh - 14, hero["fig"], "sans_bold_11", hero["color"])
        # border
        rect(x, y0, pw, 1, INK)
        rect(x, y0 + hh - 1, pw, 1, INK)
        rect(x, y0, 1, hh, INK)
        rect(x + pw - 1, y0, 1, hh, INK)


def grid():
    y0 = 340
    draw_text(MX, y0 + 2, "THE DAY IN 20 STORIES", "sans_bold_14", INK)
    draw_text(MX + CW - text_w("NUMBERED 4-23", "sans_bold_12"), y0 + 4,
              "NUMBERED 4-23", "sans_bold_12", GREY)
    hline(MX, y0 + 20, CW, INK)
    gy = y0 + 28
    cols, rows = 4, 5
    cgap = 10
    cw = (CW - (cols - 1) * cgap) // cols
    rh = 60
    for idx, (num, region, head, summ) in enumerate(GRID):
        col, row = idx % cols, idx // cols
        x = MX + col * (cw + cgap)
        y = gy + row * rh
        # number badge
        rect(x, y, 22, 22, RED)
        n = str(num)
        draw_text(x + (22 - text_w(n, "sans_bold_14")) // 2, y + 4, n,
                  "sans_bold_14", WHITE)
        # region tag
        draw_text(x + 28, y + 2, region, "sans_bold_11", RED)
        # headline (2 lines)
        ty = y + 16
        for ln in wrap(head, "sans_bold_11", cw - 28)[:2]:
            draw_text(x + 28, ty, ln, "sans_bold_11", INK)
            ty += 12
        # summary (2 lines)
        for ln in wrap(summ, "sans_10", cw - 28)[:2]:
            draw_text(x + 28, ty, ln, "sans_10", (60, 60, 60))
            ty += 10


def world_map():
    y0 = 676
    draw_text(MX, y0 + 2, "WHERE IT HAPPENED", "sans_bold_14", INK)
    draw_text(MX + CW - text_w("12 STORIES PINNED  -  NUMBERS MATCH THE GRID",
                               "sans_bold_12"), y0 + 4,
              "12 STORIES PINNED  -  NUMBERS MATCH THE GRID", "sans_bold_12", GREY)
    hline(MX, y0 + 20, CW, INK)
    mx, my, mw, mh = MX, y0 + 28, CW, 124
    rect(mx, my, mw, mh, (232, 240, 246))
    cell_w = mw / MAP_COLS
    cell_h = mh / MAP_ROWS_N
    for r, ranges in enumerate(_MAP_ROWS):
        for (a, b) in ranges:
            for c in range(a, b + 1):
                dx = int(mx + (c + 0.5) * cell_w)
                dy = int(my + (r + 0.5) * cell_h)
                rect(dx - 1, dy - 1, 2, 2, (70, 100, 140))
    # pins
    for (num, lon, lat) in PINS:
        px = int(mx + (lon + 180) / 360 * mw)
        py = int(my + (MAP_LAT_TOP - lat) / (MAP_LAT_TOP - MAP_LAT_BOT) * mh)
        circle(px, py, 8, RED, fill=True)
        circle(px, py, 8, WHITE)
        n = str(num)
        draw_text(px - text_w(n, "sans_bold_11") // 2, py - 5, n,
                  "sans_bold_11", WHITE)


def also_on():
    y0 = 836
    draw_text(MX, y0 + 2, "ALSO ON", "sans_bold_14", INK)
    draw_text(MX + CW - text_w("13 MORE  -  NUMBERED 24-36", "sans_bold_12"),
              y0 + 4, "13 MORE  -  NUMBERED 24-36", "sans_bold_12", GREY)
    hline(MX, y0 + 20, CW, INK)
    ay = y0 + 30
    col_w = CW // 2 - 12
    for i, (num, s) in enumerate(ALSO_ON):
        col = 0 if i < 7 else 1
        row = i if i < 7 else i - 7
        x = MX + col * (col_w + 24)
        y = ay + row * 14
        draw_text(x, y, str(num) + ".", "sans_bold_11", RED)
        draw_text(x + 26, y, s, "sans_11", INK)


def ticker():
    y0 = 964
    rect(0, y0, W, 24, NAVY)
    center_text(W // 2, y0 + 6,
                "MARKETS:  S&P 500 -3.70%  -  NASDAQ -5.28%  -  NIKKEI -5.06%  -  GOLD -4%  -  BRENT $90  -  BITCOIN -24% (NOV)  -  SENSEX +2.3%",
                "sans_bold_12", WHITE)


def footer():
    y0 = 988
    center_text(W // 2, y0 + 2,
                "All stories first reported or occurring on Friday 20 November 2026, any time zone.",
                "sans_10", GREY)
    center_text(W // 2, y0 + 13,
                "TIMELINE: OVERNIGHT Kyiv barrage  -  MORNING Akvan landfall  -  AFTERNOON S&P 500 enters correction  -  DAY ICJ genocide ruling.",
                "sans_10", GREY)
    center_text(W // 2, y0 + 24,
                "Drawn by a program. No photograph. Figures as reported by the outlets named above.  -  make.fun news-image-20261120",
                "sans_9", GREY)


def render(out_path):
    rect(0, 0, W, H, PAPER)
    masthead()
    verify_strip()
    heroes()
    grid()
    world_map()
    also_on()
    ticker()
    footer()
    return write_png(out_path)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    n = render(out)
    print("wrote", out, n, "bytes")
