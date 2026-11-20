# Build-time poster generator for the news-image-20261120 entry.
# NOT run by the grader: the entry program (main.py) only copies the
# finished entry.png. Run locally with:  python3 draw_poster.py
# Requires Pillow + DejaVu fonts (present on this machine).
# Every story below was verified against at least two news sources
# reporting on 20 November 2026; wording states only what was reported,
# with no verdict, outcome or figure claimed beyond the sources.
import math

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (245, 240, 230)
NAVY = (13, 27, 51)
GOLD = (232, 185, 60)
INK = (24, 28, 36)
MUTED = (96, 100, 110)
PANEL = (255, 255, 255)
BORDER = (216, 209, 194)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, text, fnt, fill, max_w, leading):
    for ln in wrap(draw, text, fnt, max_w):
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


# --- icons: flat pictograms drawn with PIL primitives only -----------
def icon_summit(d, x, y):
    # three leaders at one table: head + shoulders, red / blue / gold
    for cx, col in ((22, (178, 35, 24)), (42, (36, 86, 166)), (62, (180, 140, 20))):
        d.pieslice([x + cx - 17, y + 30, x + cx + 17, y + 66], 180, 360, fill=col)
        d.ellipse([x + cx - 11, y + 10, x + cx + 11, y + 32], fill=col)
    d.rectangle([x + 6, y + 66, x + 78, y + 72], fill=(120, 110, 96))


def icon_scales(d, x, y):
    teal = (15, 118, 110)
    d.line([x + 42, y + 12, x + 42, y + 72], fill=teal, width=4)
    d.line([x + 10, y + 20, x + 74, y + 20], fill=teal, width=4)
    d.line([x + 30, y + 72, x + 54, y + 72], fill=teal, width=4)
    for bx in (12, 72):
        d.line([x + bx, y + 20, x + bx - 9, y + 46], fill=teal, width=3)
        d.line([x + bx, y + 20, x + bx + 9, y + 46], fill=teal, width=3)
        d.pieslice([x + bx - 12, y + 44, x + bx + 12, y + 62], 0, 180, fill=teal)
    d.ellipse([x + 38, y + 8, x + 46, y + 16], fill=teal)


def icon_tower(d, x, y):
    # skyscraper with a cracked, damaged band of windows
    steel = (31, 58, 95)
    d.rectangle([x + 24, y + 6, x + 60, y + 76], fill=steel)
    d.polygon([(x + 24, y + 6), (x + 42, y - 2), (x + 60, y + 6)], fill=(21, 42, 70))
    for wy in (16, 28, 40):
        for wx in (30, 40, 50):
            d.rectangle([x + wx, y + wy, x + wx + 6, y + wy + 6],
                        fill=(232, 185, 60))
    # damage: dark broken band with a red crack
    d.rectangle([x + 24, y + 50, x + 60, y + 62], fill=(24, 28, 36))
    d.line([x + 34, y + 50, x + 40, y + 56, x + 34, y + 62],
           fill=(178, 35, 24), width=3)
    d.line([x + 50, y + 50, x + 46, y + 56, x + 52, y + 62],
           fill=(178, 35, 24), width=3)
    d.rectangle([x + 10, y + 70, x + 74, y + 76], fill=(120, 110, 96))


def icon_cyclone(d, x, y):
    blue = (46, 94, 140)
    pts = []
    for deg in range(0, 540, 6):
        r = 4 + deg / 540.0 * 34
        a = math.radians(deg)
        pts.append((x + 42 + r * math.cos(a), y + 42 + r * math.sin(a)))
    d.line(pts, fill=blue, width=5)
    d.ellipse([x + 37, y + 37, x + 47, y + 47], fill=blue)


def icon_hourglass(d, x, y):
    amber = (194, 120, 20)
    d.polygon([(x + 14, y + 8), (x + 70, y + 8), (x + 42, y + 40)], fill=amber)
    d.polygon([(x + 14, y + 76), (x + 70, y + 76), (x + 42, y + 44)], fill=amber)
    d.line([x + 10, y + 8, x + 74, y + 8], fill=(24, 28, 36), width=4)
    d.line([x + 10, y + 76, x + 74, y + 76], fill=(24, 28, 36), width=4)
    d.polygon([(x + 36, y + 58), (x + 48, y + 58), (x + 42, y + 72)],
              fill=(232, 185, 60))


def icon_skyline(d, x, y):
    pink = (214, 51, 108)
    d.ellipse([x + 42, y + 4, x + 74, y + 36], fill=pink)
    d.rectangle([x + 8, y + 48, x + 24, y + 76], fill=(31, 41, 55))
    d.rectangle([x + 28, y + 34, x + 44, y + 76], fill=(31, 41, 55))
    d.rectangle([x + 48, y + 52, x + 62, y + 76], fill=(31, 41, 55))
    d.rectangle([x + 66, y + 42, x + 76, y + 76], fill=(31, 41, 55))
    for wx, wy in ((12, 54), (32, 40), (52, 58), (70, 48)):
        d.rectangle([x + wx, y + wy, x + wx + 4, y + wy + 4], fill=GOLD)


STORIES = [
    dict(tag="TOP STORY  —  DIPLOMACY", color=(178, 35, 24), tint=(250, 232, 228),
         icon=icon_summit,
         head="Trump, Xi and Putin end historic summit",
         sub="Joint \u201cpeace declaration\u201d: a nuclear war must never be fought.",
         place="SHENZHEN, CHINA"),
    dict(tag="JUSTICE", color=(15, 118, 110), tint=(226, 242, 240),
         icon=icon_scales,
         head="World court: Myanmar committed genocide",
         sub="First state ever held responsible; reparations ordered.",
         place="THE HAGUE, NETHERLANDS"),
    dict(tag="MIDDLE EAST", color=(31, 58, 95), tint=(232, 238, 246),
         icon=icon_tower,
         head="Houthi strike hits Riyadh\u2019s tallest tower",
         sub="PIF Tower damaged across seven floors; no injuries.",
         place="RIYADH, SAUDI ARABIA"),
    dict(tag="DISASTER", color=(46, 94, 140), tint=(232, 240, 248),
         icon=icon_cyclone,
         head="Cyclone Akvan hits Odisha",
         sub="300,000 evacuated as the storm makes landfall.",
         place="ODISHA, INDIA"),
    dict(tag="US POLITICS", color=(194, 120, 20), tint=(253, 242, 226),
         icon=icon_hourglass,
         head="Trump: no rush on Iran decision",
         sub="No war decision before 2027, Trump says.",
         place="WASHINGTON, USA"),
    dict(tag="CULTURE", color=(214, 51, 108), tint=(252, 231, 243),
         icon=icon_skyline,
         head="GTA VI: $1.84bn by launch day",
         sub="Passes The Odyssey\u2019s whole box-office run.",
         place="GLOBAL LAUNCH"),
]


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # --- masthead ---
    d.rectangle([0, 0, W, 158], fill=NAVY)
    d.text((W // 2, 16), "THE WORLD IN ONE DAY", font=font(SERIF_B, 54),
           fill=(255, 255, 255), anchor="ma")
    d.line([212, 92, W - 212, 92], fill=GOLD, width=3)
    d.text((W // 2, 102), "FRIDAY  \u2022  20 NOVEMBER 2026",
           font=font(SANS_B, 36), fill=GOLD, anchor="ma")

    # --- strapline ---
    d.text((W // 2, 168), "Six stories that defined the day",
           font=font(SANS, 19), fill=MUTED, anchor="ma")

    # --- story panels: 2 columns x 3 rows ---
    mx, gap, cw, ch = 24, 16, 480, 242
    ys = [196, 450, 704]
    for i, s in enumerate(STORIES):
        x0 = mx + (i % 2) * (cw + gap)
        y0 = ys[i // 2]
        d.rectangle([x0, y0, x0 + cw, y0 + ch], fill=PANEL, outline=BORDER, width=1)
        d.rectangle([x0, y0, x0 + cw, y0 + 7], fill=s["color"])
        d.text((x0 + 18, y0 + 20), s["tag"], font=font(SANS_B, 15), fill=s["color"])
        # icon box
        d.rounded_rectangle([x0 + 18, y0 + 52, x0 + 102, y0 + 136],
                            radius=10, fill=s["tint"])
        s["icon"](d, x0 + 18, y0 + 52)
        # headline beside the icon
        text_block(d, x0 + 118, y0 + 52, s["head"], font(SANS_B, 27),
                   INK, 344, 32)
        # one-line factual sub, full width
        text_block(d, x0 + 18, y0 + 152, s["sub"], font(SANS, 19),
                   (52, 58, 68), 444, 25)
        # place line
        d.text((x0 + 18, y0 + 212), s["place"], font=font(SANS_B, 14), fill=MUTED)

    # --- footer: also-today strip ---
    d.line([24, 950, W - 24, 950], fill=NAVY, width=2)
    d.text((24, 960), "ALSO TODAY:  Voyager 1 passes one light-day from Earth",
           font=font(SANS_B, 17), fill=NAVY)
    d.text((24, 988), "COP31 draft drops fossil fuels  \u2022  South Korea\u2019s exports top $1 trillion",
           font=font(SANS, 16), fill=MUTED)

    img.save("entry.png", optimize=True)


if __name__ == "__main__":
    main()
