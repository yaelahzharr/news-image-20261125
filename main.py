#!/usr/bin/env python3
"""World news of Wednesday 25 November 2026, summed up in one image.

Draws a deterministic newspaper front page (1024x1024 PNG) with the day's
six biggest verified stories and writes it to $MAKEFUN_OUTPUT_DIR/entry.png
(default: ./entry.png). Python 3.13, standard library only: the PNG is
encoded by hand with zlib + struct and the text is drawn with a 5x7 bitmap
font, so the program needs no network and no third-party packages, and two
runs always produce the same bytes.
"""

import os
import struct
import zlib

# ----------------------------------------------------------------- palette
CREAM = (247, 241, 227)   # newspaper background
INK = (26, 26, 26)        # ink black
RED = (185, 28, 28)       # accent red
GREY = (120, 113, 100)    # rules / secondary text
WHITE = (255, 255, 255)

W, H = 1024, 1024
MARGIN = 48

# --------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows, each row 5 bits (bit 4 = leftmost column).
# Uppercase letters, digits and common punctuation; draw_text() uppercases.
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 0x0C, 0x0C),
    ",": (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    ":": (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    ";": (0, 0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04),
    "-": (0, 0, 0, 0x1F, 0, 0, 0),
    "/": (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    '"': (0x0A, 0x0A, 0x0A, 0, 0, 0, 0),
    "%": (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "+": (0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0),
    "=": (0, 0, 0x1F, 0, 0x1F, 0, 0),
    "_": (0, 0, 0, 0, 0, 0, 0x1F),
    "*": (0, 0x04, 0x15, 0x0E, 0x15, 0x04, 0),
    "#": (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A),
    "@": (0x0E, 0x11, 0x17, 0x15, 0x16, 0x10, 0x0E),
}
CHAR_W, CHAR_H = 6, 7  # 5 glyph columns + 1 spacing column; glyph height

# ------------------------------------------------------------- the news ---
# The verified world news of Wednesday 25 November 2026:
# (category, headline, one-sentence summary). Headlines wrap to at most
# 2 lines and summaries to at most 3 lines at the sizes drawn below;
# test_wrap() in the build notes asserts this, and draw_page() draws every
# wrapped line, so nothing is silently cut.
NEWS = [
    ("WORLD", "Tankers Hit Mines in Hormuz Strait",
     "Two oil tankers struck naval mines, exploded and caught fire "
     "in the Strait of Hormuz."),
    ("TECHNOLOGY", "Huawei Convicted of Stealing Trade Secrets",
     "A US jury convicted Huawei of trade-secret theft, fraud and "
     "sanctions violations."),
    ("ECONOMY", "Asian Markets Plunge; Dow Tops 50,000",
     "South Korea's KOSPI fell 6.2% while the Dow closed above "
     "50,000 for the first time."),
    ("POLITICS", "Australia Signs Pacific Security Treaty",
     "Australia and Solomon Islands signed a treaty barring foreign "
     "military bases there."),
    ("SPACE", "Pakistan Astronaut Reaches Space Station",
     "Shenzhou-24 docked with Tiangong, carrying Pakistan's first "
     "astronaut into orbit."),
    ("SPORT", "Senegal Regains Africa Cup Title",
     "Sport's highest court restored Senegal's Africa Cup of "
     "Nations title on appeal."),
]
TITLE = "THE WORLD TODAY"
DATE_LINE = "WEDNESDAY, NOVEMBER 25, 2026"
TOP_STORY = "TOP STORY: TANKERS HIT MINES IN HORMUZ STRAIT"


# ---------------------------------------------------------------- canvas ---
class Canvas:
    """An RGB pixel buffer with minimal drawing primitives."""

    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bytes(bg) * (w * h))

    def rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x0 >= x1 or y0 >= y1:
            return
        row = bytes(color) * (x1 - x0)
        stride = self.w * 3
        for yy in range(y0, y1):
            i = yy * stride + x0 * 3
            self.px[i:i + len(row)] = row

    def hline(self, x, y, w, color, thick=1):
        self.rect(x, y, w, thick, color)

    def text_width(self, text, scale):
        return len(text) * CHAR_W * scale

    def draw_text(self, text, x, y, color, scale=2):
        """Draw text (uppercased) with the 5x7 bitmap font."""
        cx = x
        for ch in text.upper().replace("\u2014", "-"):
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += CHAR_W * scale
        return cx

    def wrap(self, text, max_width, scale):
        """Split text into lines that fit within max_width pixels."""
        words, lines, cur = text.split(), [], ""
        for word in words:
            trial = f"{cur} {word}".strip()
            if self.text_width(trial, scale) <= max_width:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines


# ------------------------------------------------------------ PNG writer ---
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    return out + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def write_png(canvas, path):
    """Write the RGB canvas as a truecolor PNG (filter 0 per scanline)."""
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)  # filter: None
        raw += canvas.px[y * stride:(y + 1) * stride]
    png = (b"\x89PNG\r\n\x1a\n"
           + _chunk(b"IHDR", ihdr)
           + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + _chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)


# ---------------------------------------------------------------- drawing --
def draw_page():
    c = Canvas(W, H, CREAM)

    # --- masthead ---
    c.rect(0, 0, W, 10, RED)                                   # top rule
    c.draw_text(TITLE, MARGIN, 34, INK, scale=6)               # nameplate
    c.draw_text(DATE_LINE, MARGIN, 90, RED, scale=3)           # the day
    c.hline(MARGIN, 126, W - 2 * MARGIN, INK, thick=3)
    c.hline(MARGIN, 132, W - 2 * MARGIN, GREY, thick=1)

    # --- top story strip ---
    c.rect(MARGIN, 146, W - 2 * MARGIN, 46, RED)
    strip_w = c.text_width(TOP_STORY, 2)
    c.draw_text(TOP_STORY, (W - strip_w) // 2, 162, WHITE, scale=2)

    # --- six story cards: 2 columns x 3 rows ---
    grid_y = 216
    gap = 20
    box_w = (W - 2 * MARGIN - gap) // 2
    box_h = 236  # 3 rows end at y=944, above the footer rule (968)
    for i, (cat, headline, summary) in enumerate(NEWS[:6]):
        col, row = i % 2, i // 2
        bx = MARGIN + col * (box_w + gap)
        by = grid_y + row * (box_h + gap)

        c.rect(bx, by, box_w, box_h, WHITE)                    # card
        c.rect(bx, by, box_w, 6, RED)                          # red strip
        c.rect(bx, by, box_w, 2, INK)                          # frame
        c.rect(bx, by + box_h - 2, box_w, 2, INK)
        c.rect(bx, by, 2, box_h, INK)
        c.rect(bx + box_w - 2, by, 2, box_h, INK)

        inner = bx + 20
        text_w = box_w - 40
        y = by + 24
        c.draw_text(cat, inner, y, RED, scale=2)               # category
        y += 7 * 2 + 16
        for line in c.wrap(headline, text_w, scale=3):         # headline
            c.draw_text(line, inner, y, INK, scale=3)
            y += 7 * 3 + 6
        y += 6
        for line in c.wrap(summary, text_w, scale=2):          # summary
            c.draw_text(line, inner, y, INK, scale=2)
            y += 7 * 2 + 5

    # --- footer ---
    c.hline(MARGIN, H - 56, W - 2 * MARGIN, GREY, thick=1)
    c.draw_text("THE WORLD TODAY - WEDNESDAY, NOVEMBER 25, 2026",
                MARGIN, H - 44, GREY, scale=2)
    return c


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", ".")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    write_png(draw_page(), path)
    print(f"OK: {path} (1024x1024)")


if __name__ == "__main__":
    main()
