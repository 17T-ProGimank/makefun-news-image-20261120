"""Draw the news-image-20261120 poster: one 1024x1024 PNG.

Editorial broadsheet for Friday 20 November 2026: a navy masthead with
the date, six story panels (2 x 3) each with a flat vector icon, a
headline and one factual line, and a footer strip with three more items.

Build-time only: Pillow + DejaVu fonts. Deterministic -- no randomness,
no clock, no network. Run:  python3 draw_poster.py  ->  entry.png
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "entry.png"

W = H = 1024

PAPER = (246, 241, 231)      # warm newsprint
INK = (26, 26, 26)           # near-black text
NAVY = (22, 35, 63)          # masthead / footer band
GOLD = (217, 164, 65)        # date line, rules
CARD = (255, 255, 255)
CARD_LINE = (216, 210, 194)
GREY = (74, 74, 74)          # factual line
WHITE = (255, 255, 255)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")


def font(name, size):
    """Load a DejaVu font, falling back to Pillow's default."""
    path = FONT_DIR / name
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.load_default(size=size)


SERIF_BOLD = font("DejaVuSerif-Bold.ttf", 62)
SANS_BOLD = font("DejaVuSans-Bold.ttf", 27)
SANS = font("DejaVuSans.ttf", 19)
KICKER_FONT = font("DejaVuSans-Bold.ttf", 17)
DATE_FONT = font("DejaVuSans-Bold.ttf", 30)
FOOT_FONT = font("DejaVuSans.ttf", 19)
FOOT_BOLD = font("DejaVuSans-Bold.ttf", 19)


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap using real glyph widths."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def centre(draw, y, text, fnt, fill, width=W):
    draw.text((width / 2, y), text, font=fnt, fill=fill, anchor="ma")


# ---------------------------------------------------------------- icons
# Each draws a flat pictogram inside a square of side `s` centred at
# (cx, cy), in the story colour. All coordinates are computed from the
# centre, so icons stay put if the panel geometry changes.

def icon_leaders(d, cx, cy, s, color):
    r = s * 0.17
    gap = s * 0.30
    for i, dx in enumerate((-gap, 0, gap)):
        fill = (color, (31, 97, 141), (183, 119, 14))[i]
        d.ellipse([cx + dx - r, cy - r, cx + dx + r, cy + r], fill=fill)
        d.ellipse([cx + dx - r * 0.45, cy - r * 0.75,
                   cx + dx + r * 0.45, cy + r * 0.05], fill=WHITE)
    d.line([cx - s * 0.42, cy + s * 0.34, cx + s * 0.42, cy + s * 0.34],
           fill=color, width=5)


def icon_scales(d, cx, cy, s, color):
    top = cy - s * 0.34
    d.line([cx, top, cx, cy + s * 0.30], fill=color, width=5)
    d.ellipse([cx - 6, top - 12, cx + 6, top], fill=color)
    d.line([cx - s * 0.36, top + 4, cx + s * 0.36, top + 4],
           fill=color, width=5)
    for sign in (-1, 1):
        px = cx + sign * s * 0.36
        d.line([px, top + 4, px, top + s * 0.22], fill=color, width=3)
        d.polygon([(px - s * 0.16, top + s * 0.22),
                   (px + s * 0.16, top + s * 0.22),
                   (px, top + s * 0.34)], fill=color)
    d.line([cx - s * 0.22, cy + s * 0.34, cx + s * 0.22, cy + s * 0.34],
           fill=color, width=5)


def icon_tower(d, cx, cy, s, color):
    x0, x1 = cx - s * 0.13, cx + s * 0.13
    y0, y1 = cy - s * 0.34, cy + s * 0.34
    d.rectangle([x0, y0, x1, y1], fill=color)
    for row in range(5):
        for col in range(2):
            wx = x0 + 7 + col * 12
            wy = y0 + 8 + row * 11
            d.rectangle([wx, wy, wx + 6, wy + 6], fill=WHITE)
    burst = (217, 58, 32)
    bx, by = x1 + s * 0.10, y0 + s * 0.02
    for dx, dy in ((0, -1), (1, -1), (1, 0), (1, 1), (0, 1)):
        d.line([bx, by, bx + dx * 16, by + dy * 16], fill=burst, width=4)


def icon_cyclone(d, cx, cy, s, color):
    import math
    pts = []
    turns = 2.6
    steps = 90
    for i in range(steps + 1):
        t = i / steps * turns * 2 * math.pi
        r = s * 0.36 * i / steps
        pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
    d.line(pts, fill=color, width=5, joint="curve")
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=color)


def icon_hourglass(d, cx, cy, s, color):
    hw, hh = s * 0.30, s * 0.30
    d.polygon([(cx - hw, cy - hh), (cx + hw, cy - hh), (cx, cy)],
              outline=color, width=4)
    d.polygon([(cx - hw, cy + hh), (cx + hw, cy + hh), (cx, cy)],
              outline=color, width=4)
    d.line([cx, cy - 4, cx, cy + hh - 6], fill=color, width=4)
    for dx, dy in ((-8, 12), (7, 16), (0, 20)):
        d.ellipse([cx + dx - 2, cy + dy - 2, cx + dx + 2, cy + dy + 2],
                  fill=color)


def icon_skyline(d, cx, cy, s, color):
    base = cy + s * 0.32
    heights = (0.42, 0.62, 0.34, 0.55, 0.44)
    bw = s * 0.15
    x = cx - s * 0.40
    for h in heights:
        top = base - s * h
        d.rectangle([x, top, x + bw, base], fill=color)
        for wy in range(int(top) + 6, int(base) - 6, 12):
            d.rectangle([x + 4, wy, x + 8, wy + 5], fill=WHITE)
        x += bw + 4
    sx, sy = cx + s * 0.28, cy - s * 0.30
    d.ellipse([sx - 5, sy - 5, sx + 5, sy + 5], fill=(217, 164, 65))


ICONS = {
    "leaders": icon_leaders,
    "scales": icon_scales,
    "tower": icon_tower,
    "cyclone": icon_cyclone,
    "hourglass": icon_hourglass,
    "skyline": icon_skyline,
}

# --------------------------------------------------------------- stories
# (kicker, headline, one factual line, icon, accent colour)
STORIES = [
    ("SUMMIT IN SHENZHEN",
     "TRUMP, XI AND PUTIN END HISTORIC SUMMIT",
     "Joint peace declaration: nuclear war must never be fought.",
     "leaders", (176, 58, 46)),
    ("THE HAGUE",
     "WORLD COURT: MYANMAR COMMITTED GENOCIDE",
     "First state ever held responsible; reparations ordered.",
     "scales", (31, 97, 141)),
    ("RIYADH",
     "HOUTHI STRIKE HITS RIYADH'S TALLEST TOWER",
     "PIF Tower damaged across seven floors, no injuries.",
     "tower", (125, 60, 152)),
    ("ODISHA, INDIA",
     "CYCLONE AKVAN HITS ODISHA",
     "300,000 evacuated as the storm makes landfall.",
     "cyclone", (20, 143, 119)),
    ("WASHINGTON",
     "TRUMP: NO RUSH ON IRAN DECISION",
     "\u2018See what happens after January 1,\u2019 he says.",
     "hourglass", (183, 119, 14)),
    ("GAMING",
     "GTA VI: $1.84BN BY LAUNCH DAY",
     "Passes The Odyssey's whole box-office run.",
     "skyline", (46, 134, 193)),
]

FOOTER = [
    "Voyager 1 passes one light-day from Earth",
    "COP31 draft drops fossil fuels",
    "South Korea exports top $1 trillion",
]


def draw_panel(d, x, y, w, h, story):
    kicker, headline, fact, icon_name, color = story
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=CARD_LINE, width=2)
    d.rectangle([x, y, x + w, y + 8], fill=color)

    pad = 18
    icon_box = 84
    ix = x + pad + icon_box // 2
    iy = y + 8 + pad + icon_box // 2
    ICONS[icon_name](d, ix, iy, icon_box, color)

    tx = x + pad + icon_box + 14
    d.text((tx, y + 8 + pad + 30), kicker, font=KICKER_FONT, fill=color)

    hy = y + 8 + pad + icon_box + 6
    lines = wrap(d, headline, SANS_BOLD, w - 2 * pad)
    for line in lines[:2]:
        d.text((x + pad, hy), line, font=SANS_BOLD, fill=INK)
        hy += 32
    fy = hy + 4
    for line in wrap(d, fact, SANS, w - 2 * pad)[:2]:
        d.text((x + pad, fy), line, font=SANS, fill=GREY)
        fy += 24


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Masthead: navy band, serif title, gold date.
    d.rectangle([0, 0, W, 168], fill=NAVY)
    centre(d, 26, "THE WORLD IN ONE DAY", SERIF_BOLD, WHITE)
    centre(d, 106, "FRIDAY  \u2022  20 NOVEMBER 2026", DATE_FONT, GOLD)
    d.rectangle([0, 168, W, 172], fill=GOLD)

    # Six panels, 2 columns x 3 rows.
    margin, gutter = 28, 20
    top, bottom = 188, 936
    pw = (W - 2 * margin - gutter) // 2
    ph = (bottom - top - 2 * gutter) // 3
    for i, story in enumerate(STORIES):
        col, row = i % 2, i // 2
        x = margin + col * (pw + gutter)
        y = top + row * (ph + gutter)
        draw_panel(d, x, y, pw, ph, story)

    # Footer strip: three more items from the day.
    d.rectangle([0, 952, W, H], fill=NAVY)
    line1 = "ALSO TODAY  \u2014  " + FOOTER[0] + "  \u2022  " + FOOTER[1]
    line2 = FOOTER[2] + " for the first time"
    centre(d, 962, line1, FOOT_FONT, WHITE)
    d.text((W / 2, 990), line2, font=FOOT_BOLD, fill=GOLD, anchor="ma")

    img.save(OUT, format="PNG")
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
