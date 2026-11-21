#!/usr/bin/env python3
"""Render the 20 November 2026 world-news front page (1024x1024 PNG).

Drawn fresh in this session with Pillow + DejaVu. Every fact on the page
was verified against at least two independent sources on 2026-11-21;
see build-log.md for the source list.
"""
import hashlib
import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 36
CONTENT_W = W - 2 * MARGIN

PAPER = (247, 243, 234)
INK = (26, 26, 26)
NAVY = (22, 35, 58)
GOLD = (201, 162, 39)
RED = (179, 38, 30)
RULE = (180, 172, 155)
MUTED = (90, 86, 76)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


F_MASTHEAD = font("DejaVuSans-Bold.ttf", 52)
F_DATE = font("DejaVuSans-Bold.ttf", 33)
F_SUB = font("DejaVuSans.ttf", 19)
F_KICKER = font("DejaVuSans-Bold.ttf", 21)
F_HEADLINE = font("DejaVuSans-Bold.ttf", 42)
F_DECK = font("DejaVuSans.ttf", 22)
F_TAG = font("DejaVuSans-Bold.ttf", 18)
F_TITLE = font("DejaVuSans-Bold.ttf", 27)
F_BODY = font("DejaVuSans.ttf", 20)
F_TITLE3 = font("DejaVuSans-Bold.ttf", 24)
F_BODY3 = font("DejaVuSans.ttf", 18)
F_ALSO = font("DejaVuSans-Bold.ttf", 20)
F_ALEAD = font("DejaVuSans-Bold.ttf", 19)
F_ADECK = font("DejaVuSans.ttf", 17)
F_SRC = font("DejaVuSans.ttf", 15)


def wrap_lines(text, fnt, width):
    """Greedy word wrap measured with the real font."""
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if fnt.getlength(trial) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, lines, fnt, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def text_height(lines, leading):
    return len(lines) * leading


img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

# ---- Masthead band -------------------------------------------------------
d.rectangle([0, 0, W, 148], fill=NAVY)
d.text((W / 2, 22), "THE WORLD IN ONE DAY", font=F_MASTHEAD,
       fill=(255, 255, 255), anchor="ma")
d.line([MARGIN, 92, W - MARGIN, 92], fill=GOLD, width=2)
d.text((W / 2, 102), "FRIDAY, 20 NOVEMBER 2026", font=F_DATE,
       fill=GOLD, anchor="ma")
# subline sits just under the band, on paper
d.text((W / 2, 154), "The day's world news — in one picture",
       font=F_SUB, fill=MUTED, anchor="ma")

y = 188

# ---- Headline story: Cyclone Akvan --------------------------------------
d.text((MARGIN, y), "INDIA  ·  CYCLONE AKVAN", font=F_KICKER, fill=RED)
y += 28
headline = "Cyclone Akvan slams India's east coast"
h_lines = wrap_lines(headline, F_HEADLINE, CONTENT_W)
assert len(h_lines) == 1, f"headline wrapped unexpectedly: {h_lines}"
y = draw_wrapped(d, MARGIN, y, h_lines, F_HEADLINE, INK, 50)
deck = ("More than 300,000 people were evacuated in Odisha as the storm "
        "crossed the coast near Gopalpur on Friday morning, with winds "
        "gusting to 90 km/h. No deaths were reported in the first assessment.")
lines = wrap_lines(deck, F_DECK, CONTENT_W)
y = draw_wrapped(d, MARGIN, y + 4, lines, F_DECK, (58, 58, 58), 28)
y += 10
d.line([MARGIN, y, W - MARGIN, y], fill=RULE, width=2)
y += 18


def story_card(x, col_w, tag, tag_color, title, body, title_fnt, body_fnt,
               title_lead, body_lead):
    """Draw one story card; return its bottom y."""
    top = y
    d.text((x, top), tag, font=F_TAG, fill=tag_color)
    t_lines = wrap_lines(title, title_fnt, col_w)
    by = top + 26
    by = draw_wrapped(d, x, by, t_lines, title_fnt, INK, title_lead)
    b_lines = wrap_lines(body, body_fnt, col_w)
    by = draw_wrapped(d, x, by + 6, b_lines, body_fnt, (58, 58, 58), body_lead)
    return by


# ---- Row A: two stories ---------------------------------------------------
col_a = (CONTENT_W - 28) // 2
row_a_top = y
end_a1 = story_card(
    MARGIN, col_a, "WAR IN EUROPE", (15, 118, 110),
    "Russian strikes kill 8 in Kyiv; missiles enter Polish airspace",
    "Overnight attacks hit bridges in the capital and a railway station "
    "in Lviv, killing two more. Poland said two missiles and a drone "
    "crossed its border.",
    F_TITLE, F_BODY, 31, 25)
end_a2 = story_card(
    MARGIN + col_a + 28, col_a, "ESTONIA", (29, 78, 216),
    "Estonia to shut its border with Russia",
    "Tallinn said the frontier will close for at least six months. "
    "Moscow accused it of building a new \u201cIron Curtain\u201d.",
    F_TITLE, F_BODY, 31, 25)
y = max(end_a1, end_a2) + 12
d.line([MARGIN, y, W - MARGIN, y], fill=RULE, width=1)
y += 12

# ---- Row B: three stories --------------------------------------------------
col_b = (CONTENT_W - 2 * 24) // 3
end_b1 = story_card(
    MARGIN, col_b, "CLIMATE", (21, 128, 61),
    "COP31 draft drops fossil fuels as talks hit final day",
    "Antalya talks face a Friday deadline with no deal in sight, after "
    "the draft dropped all mention of fossil fuels.",
    F_TITLE3, F_BODY3, 28, 23)
end_b2 = story_card(
    MARGIN + col_b + 24, col_b, "MARKETS", (180, 83, 9),
    "Anthropic slides 8.5% as stocks fall again",
    "The AI firm fell on its second day, a day after its record $81.3bn "
    "debut failed to stop the slide in US stocks.",
    F_TITLE3, F_BODY3, 28, 23)
end_b3 = story_card(
    MARGIN + 2 * (col_b + 24), col_b, "EUROPE", (109, 40, 217),
    "Young people walk out in 25 countries",
    "Tens of thousands of students protested across Europe over the "
    "cost of living, housing and military spending.",
    F_TITLE3, F_BODY3, 28, 23)
y = max(end_b1, end_b2, end_b3) + 12
d.line([MARGIN, y, W - MARGIN, y], fill=RULE, width=2)
y += 12

# ---- Also today -------------------------------------------------------------
d.text((MARGIN, y), "ALSO TODAY", font=F_ALSO, fill=RED)
y += 28
also = [
    ("Myanmar dismisses genocide ruling",
     "The government rejected the world court's finding against it over "
     "the Rohingya."),
    ("Trump: Putin \u201cwants the deal done\u201d",
     "The US president spoke to European leaders after the three-way "
     "summit in Shenzhen."),
    ("GTA 6 takes an estimated $2.36bn in a day",
     "Sensor Tower estimates 24.6m copies sold on launch day \u2014 a "
     "record. No official figures yet."),
]
also_bottom = y
for i, (lead, deck_text) in enumerate(also):
    x = MARGIN + i * (col_b + 24)
    ly = draw_wrapped(d, x, y, wrap_lines(lead, F_ALEAD, col_b),
                      F_ALEAD, INK, 24)
    ly = draw_wrapped(d, x, ly + 4, wrap_lines(deck_text, F_ADECK, col_b),
                      F_ADECK, (58, 58, 58), 21)
    also_bottom = max(also_bottom, ly)
y = also_bottom + 12
d.line([MARGIN, y, W - MARGIN, y], fill=RULE, width=1)
y += 8
d.text((W / 2, y), "Sources: IMD \u00b7 BBC \u00b7 Reuters \u00b7 UN News \u00b7 "
       "Barron's \u00b7 CNN \u00b7 Sensor Tower  \u2014  20 November 2026",
       font=F_SRC, fill=MUTED, anchor="ma")

assert y + 22 <= H, f"layout overflow: footer ends at {y + 22}"

out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "entry.png")
img.save(out_path, "PNG", optimize=True)

data = open(out_path, "rb").read()
print(f"wrote {out_path}")
print(f"size: {img.size}, bytes: {len(data)} "
      f"(limit 1048576: {'OK' if len(data) <= 1048576 else 'OVER'})")
print(f"sha256: {hashlib.sha256(data).hexdigest()}")
print(f"footer bottom: {y + 22} / {H}")
