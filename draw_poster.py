#!/usr/bin/env python3
"""Draw the world news of Friday 20 November 2026 as one poster.

Writes entry.png (1024x1024) next to this file. Deterministic: no random
numbers, no clock, no network; every string is fixed below.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = Path(__file__).resolve().parent / "entry.png"

# ---------------------------------------------------------------- palette ---
PAPER = (245, 241, 230)      # warm newsprint
INK = (17, 24, 39)           # near-black headline ink
NAVY = (15, 36, 64)          # masthead / ticker band
NAVY_SOFT = (28, 58, 96)
RED = (185, 28, 28)          # lead accent / urgency
GOLD = (232, 184, 75)        # date + rules
GRAY = (88, 94, 106)         # secondary text
CARD = (255, 255, 255)
BORDER = (214, 208, 194)
TEAL = (13, 116, 128)
AMBER = (180, 83, 9)
GREEN = (21, 128, 61)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
BOLD = FONT_DIR + "/DejaVuSans-Bold.ttf"
REG = FONT_DIR + "/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_font(draw, text, path, start, max_w):
    """Largest size (<= start) at which text fits max_w."""
    size = start
    while size > 10:
        f = font(path, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 2
    return font(path, 10)


def wrap(text, f, max_w, draw):
    """Word-wrap text into lines that fit max_w (measured, never guessed)."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_two_lines(text, f, max_w, draw):
    """Wrap to at most 2 lines, truncating the tail with an ellipsis."""
    lines = wrap(text, f, max_w, draw)
    if len(lines) <= 2:
        return lines
    head = lines[0]
    rest = " ".join(lines[1:])
    while rest and draw.textlength(rest + " \u2026", font=f) > max_w:
        rest = rest.rsplit(" ", 1)[0] if " " in rest else ""
    return [head, rest + " \u2026"] if rest else [head]


def draw_lines(draw, x, y, lines, f, fill, spacing=1.18):
    """Draw lines top-left at (x, y); return y just below the last line."""
    lh = int(f.size * spacing)
    for line in lines:
        draw.text((x, y), line, font=f, fill=fill)
        y += lh
    return y


def draw_icon(d, kind, x, y, s, color):
    """Tiny geometric icon inside an s x s box at (x, y)."""
    import math
    cx, cy = x + s // 2, y + s // 2
    if kind == "burst":  # explosion / strike
        for k in range(8):
            a = math.pi * k / 4.0
            d.line([cx + 4 * math.cos(a), cy + 4 * math.sin(a),
                    cx + (s // 2 - 1) * math.cos(a),
                    cy + (s // 2 - 1) * math.sin(a)], fill=color, width=3)
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=color)
    elif kind == "scales":  # justice
        d.line([cx, y + 2, cx, y + s - 4], fill=color, width=3)
        d.line([x + 2, y + 7, x + s - 2, y + 7], fill=color, width=3)
        d.polygon([(x + 1, y + 8), (x + 7, y + 8), (x + 4, y + 15)], fill=color)
        d.polygon([(x + s - 7, y + 8), (x + s - 1, y + 8),
                   (x + s - 4, y + 15)], fill=color)
        d.line([x + 4, y + s - 4, x + s - 4, y + s - 4], fill=color, width=3)
    elif kind == "chart":  # markets falling
        d.line([x + 2, y + 6, x + s // 2, y + s // 2,
                x + s - 4, y + s - 5], fill=color, width=3)
        d.polygon([(x + s - 4, y + s - 5), (x + s - 11, y + s - 6),
                   (x + s - 5, y + s - 12)], fill=color)
    elif kind == "dots":  # three leaders / summit
        d.line([x + 5, cy, x + s - 5, cy], fill=color, width=3)
        for px in (x + 5, cx, x + s - 5):
            d.ellipse([px - 4, cy - 4, px + 4, cy + 4], fill=color)
    elif kind == "crack":  # earthquake
        pts = [(x + 2, y + 3), (x + s // 3, y + s // 2),
               (x + s // 2, y + s // 3), (x + 2 * s // 3, y + 2 * s // 3),
               (x + s - 2, y + s - 4)]
        d.line(pts, fill=color, width=3, joint="curve")
    elif kind == "bridge":  # deal / agreement
        d.arc([x + 2, y + 8, x + s - 2, y + s + 6], start=180, end=360,
              fill=color, width=3)
        d.line([x + 3, y + s - 4, x + s - 3, y + s - 4], fill=color, width=3)
        d.line([x + 7, y + s - 10, x + 7, y + s - 4], fill=color, width=2)
        d.line([x + s - 7, y + s - 10, x + s - 7, y + s - 4],
               fill=color, width=2)


def radar(d, cx, cy, r):
    """Stylised radar scope: the lead story's graphic."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=NAVY)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GOLD, width=3)
    for rr in (int(r * 0.66), int(r * 0.38)):
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                  outline=(120, 150, 190), width=2)
    d.line([cx - r, cy, cx + r, cy], fill=(120, 150, 190), width=2)
    d.line([cx, cy - r, cx, cy + r], fill=(120, 150, 190), width=2)
    # blips: the incoming missiles, in red
    for bx, by, br in ((cx - 52, cy - 46, 7), (cx + 58, cy + 34, 7),
                       (cx + 30, cy - 62, 5)):
        d.ellipse([bx - br, by - br, bx + br, by + br], fill=RED)
    d.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], fill=RED)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(255, 255, 255))


# ------------------------------------------------------------------ copy ----
MASTHEAD = "THE WORLD IN ONE DAY"
DATE_LINE = "FRIDAY  ·  20 NOVEMBER 2026"

LEAD = {
    "kicker": "LEAD  ·  WAR IN EUROPE",
    "headline": "RUSSIAN MISSILES HIT POLAND",
    "deck": ("Two missiles and a drone land on NATO soil. PM Tusk calls it an "
             "\u201cintentional provocation\u201d; NATO chief Rutte calls it a "
             "\u201cgrave violation\u201d."),
    "fact": ("A Kh-101 cruise missile fell about 60 km from Ukraine\u2019s border."),
}

STORIES = [
    {"kicker": "UKRAINE", "color": RED, "icon": "burst",
     "headline": "Russia\u2019s biggest November strike on Kyiv",
     "fact": "404 drones and 111 missiles overnight; at least 8 killed, power and bridges hit."},
    {"kicker": "JUSTICE", "color": NAVY_SOFT, "icon": "scales",
     "headline": "World Court: Myanmar committed genocide",
     "fact": "ICJ rules the Rohingya faced state-sponsored genocide."},
    {"kicker": "MARKETS", "color": AMBER, "icon": "chart",
     "headline": "Stocks plunge as the AI rally unravels",
     "fact": "S&P 500 falls 3.7% into correction; Nikkei drops 5.06%."},
    {"kicker": "DIPLOMACY", "color": TEAL, "icon": "dots",
     "headline": "Trump, Xi and Putin meet in Shenzhen",
     "fact": "Three leaders issue a joint peace declaration; Germany warns against a \u201cnew Yalta\u201d."},
    {"kicker": "DISASTER", "color": AMBER, "icon": "crack",
     "headline": "Magnitude 6.7 quake hits central Peru",
     "fact": "Strong tremor strikes the Cerro de Pasco region."},
    {"kicker": "EUROPE", "color": GREEN, "icon": "bridge",
     "headline": "UK and EU sign new trade deals",
     "fact": "Food, carbon markets and youth mobility agreed in Brussels."},
]

TICKER = "MARKETS   ·   S&P 500 \u25bc 3.7%      NIKKEI \u25bc 5.06%      FTSE 100 \u25bc 1.0%      BRENT \u25b2 0.5%"


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---------------------------------------------------------- masthead ----
    d.rectangle([0, 0, W, 140], fill=NAVY)
    f_title = fit_font(d, MASTHEAD, BOLD, 64, W - 80)
    tw = d.textlength(MASTHEAD, font=f_title)
    d.text(((W - tw) / 2, 20), MASTHEAD, font=f_title, fill=(255, 255, 255))
    f_date = font(BOLD, 30)
    dw = d.textlength(DATE_LINE, font=f_date)
    d.text(((W - dw) / 2, 88), DATE_LINE, font=f_date, fill=GOLD)
    d.rectangle([0, 140, W, 144], fill=GOLD)

    # -------------------------------------------------------- lead story ----
    lx, ly, lw, lh = 28, 156, W - 56, 316
    d.rectangle([lx, ly, lx + lw, ly + lh], fill=CARD, outline=BORDER, width=2)
    d.rectangle([lx, ly, lx + 12, ly + lh], fill=RED)

    tx = lx + 32
    f_kick = font(BOLD, 20)
    d.text((tx, ly + 18), LEAD["kicker"], font=f_kick, fill=RED)
    f_head = fit_font(d, "RUSSIAN MISSILES", BOLD, 58, 680)
    hy = draw_lines(d, tx, ly + 48,
                    wrap(LEAD["headline"], f_head, 680, d),
                    f_head, INK, spacing=1.05)
    f_deck = font(REG, 24)
    dy = draw_lines(d, tx, hy + 10,
                    wrap(LEAD["deck"], f_deck, 680, d),
                    f_deck, (40, 48, 64), spacing=1.25)
    f_fact = font(REG, 19)
    draw_lines(d, tx, dy + 8,
               wrap(LEAD["fact"], f_fact, 680, d),
               f_fact, GRAY, spacing=1.25)

    radar(d, 852, 306, 98)
    f_cap = font(BOLD, 16)
    cap = "NATO TERRITORY"
    cw = d.textlength(cap, font=f_cap)
    d.text((852 - cw / 2, 418), cap, font=f_cap, fill=RED)

    # ----------------------------------------------------- supporting grid ----
    gy0, gh, gap = 486, 148, 14
    cw2 = (W - 56 - gap) // 2
    for i, s in enumerate(STORIES):
        col, row = i % 2, i // 2
        x = 28 + col * (cw2 + gap)
        y = gy0 + row * (gh + gap)
        d.rectangle([x, y, x + cw2, y + gh], fill=CARD, outline=BORDER, width=2)
        d.rectangle([x, y, x + cw2, y + 5], fill=s["color"])
        px, py = x + 16, y + 14
        f_k = font(BOLD, 16)
        d.text((px, py), s["kicker"], font=f_k, fill=s["color"])
        draw_icon(d, s["icon"], x + cw2 - 46, y + 12, 28, s["color"])
        f_h = font(BOLD, 23)
        hy2 = draw_lines(d, px, y + 40,
                         fit_two_lines(s["headline"], f_h, cw2 - 32, d),
                         f_h, INK, spacing=1.1)
        f_f = font(REG, 18)
        draw_lines(d, px, hy2 + 4,
                   fit_two_lines(s["fact"], f_f, cw2 - 32, d),
                   f_f, GRAY, spacing=1.2)

    # ------------------------------------------------------------ ticker ----
    d.rectangle([0, 972, W, H], fill=NAVY)
    f_t = fit_font(d, TICKER, BOLD, 20, W - 40)
    tw2 = d.textlength(TICKER, font=f_t)
    d.text(((W - tw2) / 2, 986), TICKER, font=f_t, fill=(255, 255, 255))

    img.save(OUT, format="PNG", optimize=True)
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
