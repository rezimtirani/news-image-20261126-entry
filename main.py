"""Front page for Thursday 26 November 2026.

Draws a newspaper front page that sums up the day's world news
in a single 1024x1024 PNG, using only the Python standard
library. The picture is built pixel by pixel: a hand-drawn 5x7
bitmap font, flat colour panels, and simple shapes for the
refinery, the parade balloons, the rocket and the small icons.
Nothing is read from the network or the clock, so two runs
write exactly the same bytes.
"""

import os
import struct
import zlib
from os.path import join

WIDTH = 1024
HEIGHT = 1024

PAPER = (246, 241, 231)
INK = (20, 20, 20)
NAVY = (22, 35, 63)
DEEPNAVY = (13, 22, 44)
RED = (179, 32, 44)
ORANGE = (232, 114, 42)
GOLD = (217, 164, 65)
SKY = (191, 211, 230)
STEEL = (74, 74, 74)
DARKGREY = (43, 43, 43)
MIDGREY = (85, 85, 85)
LIGHTGREY = (210, 205, 192)
WHITE = (255, 255, 255)
CREAM = (250, 246, 236)
BLUEBALLOON = (52, 110, 190)
YELLOWBALLOON = (240, 196, 60)
REDBALLOON = (198, 52, 52)
SEABLUE = (46, 110, 142)
SOFTINK = (90, 86, 76)

# A 5-wide, 7-tall bitmap font. Each glyph is seven rows of five
# characters; '#' is ink, '.' is blank. Uppercase only, which
# suits a newspaper front page.
FONT = {
    'A': ('.###.', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'),
    'B': ('####.', '#...#', '#...#', '####.', '#...#', '#...#', '####.'),
    'C': ('.####', '#....', '#....', '#....', '#....', '#....', '.####'),
    'D': ('####.', '#...#', '#...#', '#...#', '#...#', '#...#', '####.'),
    'E': ('#####', '#....', '#....', '####.', '#....', '#....', '#####'),
    'F': ('#####', '#....', '#....', '####.', '#....', '#....', '#....'),
    'G': ('.####', '#....', '#....', '#.###', '#...#', '#...#', '.###.'),
    'H': ('#...#', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'),
    'I': ('#####', '..#..', '..#..', '..#..', '..#..', '..#..', '#####'),
    'J': ('..###', '...#.', '...#.', '...#.', '...#.', '#..#.', '.##..'),
    'K': ('#...#', '#..#.', '#.#..', '##...', '#.#..', '#..#.', '#...#'),
    'L': ('#....', '#....', '#....', '#....', '#....', '#....', '#####'),
    'M': ('#...#', '##.##', '#.#.#', '#.#.#', '#...#', '#...#', '#...#'),
    'N': ('#...#', '##..#', '##..#', '#.#.#', '#..##', '#..##', '#...#'),
    'O': ('.###.', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'),
    'P': ('####.', '#...#', '#...#', '####.', '#....', '#....', '#....'),
    'Q': ('.###.', '#...#', '#...#', '#...#', '#.#.#', '#..#.', '.##.#'),
    'R': ('####.', '#...#', '#...#', '####.', '#.#..', '#..#.', '#...#'),
    'S': ('.####', '#....', '#....', '.###.', '....#', '....#', '####.'),
    'T': ('#####', '..#..', '..#..', '..#..', '..#..', '..#..', '..#..'),
    'U': ('#...#', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'),
    'V': ('#...#', '#...#', '#...#', '#...#', '#...#', '.#.#.', '..#..'),
    'W': ('#...#', '#...#', '#...#', '#.#.#', '#.#.#', '##.##', '#...#'),
    'X': ('#...#', '#...#', '.#.#.', '..#..', '.#.#.', '#...#', '#...#'),
    'Y': ('#...#', '#...#', '.#.#.', '..#..', '..#..', '..#..', '..#..'),
    'Z': ('#####', '....#', '...#.', '..#..', '.#...', '#....', '#####'),
    '0': ('.###.', '#..##', '#.#.#', '##..#', '#...#', '#...#', '.###.'),
    '1': ('..#..', '.##..', '..#..', '..#..', '..#..', '..#..', '.###.'),
    '2': ('.###.', '#...#', '....#', '...#.', '..#..', '.#...', '#####'),
    '3': ('####.', '....#', '....#', '.###.', '....#', '....#', '####.'),
    '4': ('...#.', '..##.', '.#.#.', '#..#.', '#####', '...#.', '...#.'),
    '5': ('#####', '#....', '####.', '....#', '....#', '#...#', '.###.'),
    '6': ('.###.', '#....', '#....', '####.', '#...#', '#...#', '.###.'),
    '7': ('#####', '....#', '...#.', '..#..', '..#..', '..#..', '..#..'),
    '8': ('.###.', '#...#', '#...#', '.###.', '#...#', '#...#', '.###.'),
    '9': ('.###.', '#...#', '#...#', '.####', '....#', '....#', '.###.'),
    ' ': ('.....', '.....', '.....', '.....', '.....', '.....', '.....'),
    '.': ('.....', '.....', '.....', '.....', '.....', '.##..', '.##..'),
    ',': ('.....', '.....', '.....', '.....', '.....', '.##..', '.#...'),
    "'": ('..#..', '..#..', '.#...', '.....', '.....', '.....', '.....'),
    ':': ('.....', '.##..', '.##..', '.....', '.##..', '.##..', '.....'),
    ';': ('.....', '.##..', '.##..', '.....', '.##..', '.##..', '.#...'),
    '!': ('..#..', '..#..', '..#..', '..#..', '..#..', '.....', '..#..'),
    '?': ('.###.', '#...#', '....#', '...#.', '..#..', '.....', '..#..'),
    '-': ('.....', '.....', '.....', '.###.', '.....', '.....', '.....'),
    '/': ('....#', '....#', '...#.', '..#..', '.#...', '#....', '#....'),
    '(': ('...#.', '..#..', '.#...', '.#...', '.#...', '..#..', '...#.'),
    ')': ('.#...', '..#..', '...#.', '...#.', '...#.', '..#..', '.#...'),
    '%': ('#...#', '#..#.', '...#.', '..#..', '.#...', '#..#.', '#...#'),
    '$': ('..#..', '.####', '#.#..', '.###.', '..#.#', '####.', '..#..'),
    '&': ('.##..', '#..#.', '#.#..', '.#...', '#.#.#', '#..#.', '.##.#'),
    '+': ('.....', '..#..', '..#..', '#####', '..#..', '..#..', '.....'),
    '=': ('.....', '.....', '#####', '.....', '#####', '.....', '.....'),
    '"': ('.#.#.', '.#.#.', '.....', '.....', '.....', '.....', '.....'),
    '•': ('.....', '.....', '.###.', '.###.', '.###.', '.....', '.....'),
    '*': ('.....', '.#.#.', '.###.', '#####', '.###.', '.#.#.', '.....'),
}

BLANK_GLYPH = ('.....', '.....', '.....', '.....', '.....', '.....', '.....')


def glyph_rows(ch):
    """Return the seven bitmap rows for one character."""
    return FONT.get(ch, BLANK_GLYPH)


def text_width(text, scale):
    """Width in pixels of a line drawn at the given scale."""
    return len(text) * 6 * scale


def wrap_words(text, max_width, scale):
    """Split text into lines that fit max_width pixels."""
    lines = []
    current = ''
    for word in text.split(' '):
        trial = word if not current else current + ' ' + word
        if text_width(trial, scale) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


class Canvas:
    """A plain RGB pixel buffer with tiny drawing helpers."""

    def __init__(self, width, height, background):
        self.w = width
        self.h = height
        self.buf = bytearray(bytes(background) * (width * height))

    def set(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            pos = (y * self.w + x) * 3
            self.buf[pos] = colour[0]
            self.buf[pos + 1] = colour[1]
            self.buf[pos + 2] = colour[2]

    def fill(self, x, y, w, h, colour):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            span = (x1 - x0) * 3
            self.buf[base:base + span] = bytes(colour) * (x1 - x0)

    def line(self, x0, y0, x1, y1, colour):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, colour)
            if x0 == x1 and y0 == y1:
                return
            step = 2 * err
            if step >= dy:
                err += dy
                x0 += sx
            if step <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, radius, colour):
        for dy in range(-radius, radius + 1):
            half = int((radius * radius - dy * dy) ** 0.5)
            self.fill(cx - half, cy + dy, half * 2 + 1, 1, colour)

    def ring(self, cx, cy, radius, colour):
        for angle in range(360):
            import math
            px = cx + int(radius * math.cos(math.radians(angle)))
            py = cy + int(radius * math.sin(math.radians(angle)))
            self.set(px, py, colour)

    def triangle(self, p0, p1, p2, colour):
        xs = [p0[0], p1[0], p2[0]]
        ys = [p0[1], p1[1], p2[1]]
        x0, x1 = min(xs), max(xs)
        y0, y1 = min(ys), max(ys)
        denom = (ys[1] - ys[2]) * (xs[0] - xs[2]) + (xs[2] - xs[1]) * (ys[0] - ys[2])
        if denom == 0:
            return
        for yy in range(y0, y1 + 1):
            for xx in range(x0, x1 + 1):
                a = ((ys[1] - ys[2]) * (xx - xs[2]) + (xs[2] - xs[1]) * (yy - ys[2])) / denom
                b = ((ys[2] - ys[0]) * (xx - xs[2]) + (xs[0] - xs[2]) * (yy - ys[2])) / denom
                c = 1.0 - a - b
                if a >= 0 and b >= 0 and c >= 0:
                    self.set(xx, yy, colour)

    def text(self, x, y, string, scale, colour):
        """Draw one line; returns the pixel width drawn."""
        string = string.upper()
        cursor = x
        for ch in string:
            rows = glyph_rows(ch)
            for row in range(7):
                for col in range(5):
                    if rows[row][col] == '#':
                        self.fill(cursor + col * scale, y + row * scale,
                                  scale, scale, colour)
            cursor += 6 * scale
        return cursor - x

    def centred(self, centre_x, y, string, scale, colour):
        start = centre_x - text_width(string, scale) // 2
        return self.text(start, y, string, scale, colour)

    def paragraph(self, x, y, string, max_width, scale, colour, gap=6):
        """Draw wrapped lines; returns the y after the last line."""
        lines = wrap_words(string, max_width, scale)
        cursor_y = y
        for line_text in lines:
            self.text(x, cursor_y, line_text, scale, colour)
            cursor_y += 7 * scale + gap
        return cursor_y


def png_chunk(tag, data):
    size = struct.pack('>I', len(data))
    crc = struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    return size + tag + data + crc


def encode_png(canvas):
    raw = bytearray()
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.buf[y * canvas.w * 3:(y + 1) * canvas.w * 3]
    header = struct.pack('>IIBBBBB', canvas.w, canvas.h, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n'
            + png_chunk(b'IHDR', header)
            + png_chunk(b'IDAT', zlib.compress(bytes(raw), 9))
            + png_chunk(b'IEND', b''))


def draw_masthead(cv):
    cv.fill(16, 16, 992, 112, NAVY)
    cv.centred(512, 40, 'THE WORLD TODAY', 7, WHITE)
    cv.fill(16, 128, 992, 6, RED)
    cv.centred(512, 144, 'THURSDAY 26 NOVEMBER 2026', 3, INK)
    cv.fill(16, 172, 992, 2, INK)


def draw_lead(cv):
    # Headline and standfirst.
    cv.text(24, 192, 'GULF IN FLAMES', 5, RED)
    cv.paragraph(24, 240, "Houthis claim strike on Saudi Arabia's biggest refinery",
                 600, 2, INK)
    # Picture: refinery under a black smoke plume.
    cv.fill(24, 300, 600, 220, SKY)
    cv.fill(24, 470, 600, 50, DARKGREY)
    # Storage tanks.
    cv.fill(330, 420, 110, 50, STEEL)
    cv.fill(330, 412, 110, 8, LIGHTGREY)
    cv.fill(460, 430, 110, 40, STEEL)
    cv.fill(460, 422, 110, 8, LIGHTGREY)
    # Distillation towers.
    cv.fill(60, 350, 36, 120, STEEL)
    cv.fill(56, 342, 44, 8, MIDGREY)
    cv.fill(120, 330, 36, 140, STEEL)
    cv.fill(116, 322, 44, 8, MIDGREY)
    cv.fill(180, 360, 36, 110, STEEL)
    cv.fill(176, 352, 44, 8, MIDGREY)
    # Pipes between the towers.
    cv.fill(96, 400, 24, 6, MIDGREY)
    cv.fill(156, 380, 24, 6, MIDGREY)
    # Flare stack with a flame.
    cv.fill(580, 330, 14, 140, DARKGREY)
    # Black smoke plume rising to the upper right.
    cv.disc(520, 330, 34, DARKGREY)
    cv.disc(548, 306, 40, INK)
    cv.disc(572, 322, 30, MIDGREY)
    cv.disc(590, 300, 34, DARKGREY)
    cv.disc(606, 316, 22, INK)
    # Flame drawn last so it shows against the smoke.
    cv.triangle((573, 330), (601, 330), (587, 292), ORANGE)
    cv.triangle((580, 330), (594, 330), (587, 306), GOLD)
    # Caption strip.
    cv.fill(24, 528, 600, 30, CREAM)
    cv.centred(324, 534, 'RAS TANURA - 550,000 BARRELS A DAY - BRENT $93.60',
               2, INK)


def draw_parade(cv):
    cv.text(648, 192, '100TH PARADE', 4, NAVY)
    cv.paragraph(648, 232, "Macy's 100th Thanksgiving parade fills New York",
                 352, 2, INK)
    # Picture: balloons over the Manhattan skyline.
    cv.fill(648, 300, 352, 220, SKY)
    # Skyline.
    cv.fill(648, 440, 60, 80, NAVY)
    cv.fill(712, 420, 44, 100, DEEPNAVY)
    cv.fill(760, 450, 70, 70, NAVY)
    cv.fill(834, 410, 52, 110, DEEPNAVY)
    cv.fill(890, 445, 56, 75, NAVY)
    cv.fill(950, 425, 50, 95, DEEPNAVY)
    # Windows.
    for bx, by in ((660, 455), (680, 475), (722, 435), (742, 465),
                   (775, 465), (800, 485), (848, 425), (868, 455),
                   (905, 460), (925, 485), (962, 440), (982, 470)):
        cv.fill(bx, by, 8, 10, GOLD)
    # Balloons: blue dog, yellow balloon, red balloon.
    cv.disc(740, 360, 44, BLUEBALLOON)
    cv.disc(716, 322, 14, BLUEBALLOON)
    cv.disc(764, 322, 14, BLUEBALLOON)
    cv.disc(726, 352, 7, WHITE)
    cv.disc(754, 352, 7, WHITE)
    cv.disc(728, 354, 3, INK)
    cv.disc(752, 354, 3, INK)
    cv.disc(890, 350, 38, YELLOWBALLOON)
    cv.disc(890, 350, 14, ORANGE)
    cv.disc(962, 395, 30, REDBALLOON)
    # Strings down to the street.
    cv.line(740, 404, 730, 470, INK)
    cv.line(890, 388, 880, 470, INK)
    cv.line(962, 425, 955, 470, INK)
    # Confetti.
    for cx, cy, col in ((668, 330, RED), (700, 360, GOLD), (800, 320, RED),
                        (830, 380, BLUEBALLOON), (920, 320, GOLD),
                        (980, 350, RED), (700, 410, GOLD), (840, 440, RED)):
        cv.fill(cx, cy, 8, 8, col)
    # Caption strip.
    cv.fill(648, 528, 352, 30, CREAM)
    cv.centred(824, 534, '100 GIANT BALLOONS - 3M IN NYC', 2, INK)


def draw_space(cv):
    cv.fill(24, 580, 976, 190, NAVY)
    # Stars.
    for sx, sy in ((60, 610), (120, 740), (300, 600), (420, 750),
                   (560, 610), (700, 740), (840, 600), (950, 740),
                   (200, 700), (640, 700), (900, 640), (380, 640)):
        cv.fill(sx, sy, 4, 4, WHITE)
    # Moon.
    cv.disc(940, 640, 34, LIGHTGREY)
    cv.disc(928, 630, 8, MIDGREY)
    cv.disc(950, 650, 6, MIDGREY)
    # Rocket on the left.
    cv.fill(96, 630, 34, 110, WHITE)
    cv.triangle((96, 630), (130, 630), (113, 592), RED)
    cv.fill(96, 668, 34, 6, RED)
    cv.triangle((96, 700), (80, 768), (96, 740), RED)
    cv.triangle((130, 700), (146, 768), (130, 740), RED)
    cv.triangle((104, 740), (122, 740), (113, 768), ORANGE)
    cv.triangle((108, 740), (118, 740), (113, 758), GOLD)
    cv.disc(113, 650, 9, SKY)
    cv.ring(113, 650, 9, NAVY)
    # Headline and standfirst.
    cv.text(170, 606, "PAKISTAN'S FIRST ASTRONAUT", 3, WHITE)
    cv.text(170, 644, "HEADS FOR CHINA'S TIANGONG STATION", 3, WHITE)
    cv.paragraph(170, 690, 'Muhammad Zeeshan Ali joins Shenzhou-24 - first '
                 'foreign visitor to Tiangong', 780, 2, LIGHTGREY)


def draw_footer(cv):
    cv.fill(16, 980, 992, 2, INK)
    cv.centred(512, 988, '26 NOV 2026 - SIX STORIES FROM AROUND THE WORLD',
               2, SOFTINK)


def main():
    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', 'output')
    os.makedirs(out_dir, exist_ok=True)
    cv = Canvas(WIDTH, HEIGHT, PAPER)
    # Outer frame.
    cv.fill(0, 0, WIDTH, 10, INK)
    cv.fill(0, HEIGHT - 10, WIDTH, 10, INK)
    cv.fill(0, 0, 10, HEIGHT, INK)
    cv.fill(WIDTH - 10, 0, 10, HEIGHT, INK)
    draw_masthead(cv)
    draw_lead(cv)
    draw_parade(cv)
    draw_space(cv)
    draw_bottom_strip(cv)
    draw_footer(cv)
    data = encode_png(cv)
    if len(data) > 1024 * 1024:
        raise ValueError('entry.png is %d bytes, over the 1 MiB limit'
                         % len(data))
    target = join(out_dir, 'entry.png')
    with open(target, 'wb') as handle:
        handle.write(data)
    return 0


def draw_bottom_strip(cv):
    """Three small stories with a tiny icon each."""
    columns = [
        (24, 'US READIES NEW GLOBAL TARIFF PLAN', 'bars'),
        (354, 'ISRAEL STRIKE IN GAZA STRAINS CEASEFIRE', 'burst'),
        (684, 'TWO TANKERS HIT MINES IN STRAIT OF HORMUZ', 'tanker'),
    ]
    for x, headline, icon in columns:
        cv.fill(x, 790, 316, 2, INK)
        if icon == 'bars':
            # Rising bar chart for the tariff plan.
            cv.line(x + 40, 870, x + 40, 800, INK)
            cv.line(x + 40, 870, x + 280, 870, INK)
            cv.fill(x + 70, 840, 30, 30, NAVY)
            cv.fill(x + 120, 820, 30, 50, SEABLUE)
            cv.fill(x + 170, 800, 30, 70, RED)
            cv.fill(x + 220, 850, 30, 20, GOLD)
        elif icon == 'burst':
            # Starburst for the Gaza strike.
            cx, cy = x + 158, 835
            for dx, dy in ((0, -34), (24, -24), (34, 0), (24, 24),
                           (0, 34), (-24, 24), (-34, 0), (-24, -24)):
                cv.line(cx, cy, cx + dx, cy + dy, RED)
            cv.disc(cx, cy, 12, RED)
            cv.disc(cx, cy, 5, GOLD)
        else:
            # Oil tanker and a spiked mine for Hormuz.
            cv.fill(x + 40, 830, 200, 26, SEABLUE)
            cv.triangle((x + 240, 830), (x + 270, 843), (x + 240, 856),
                        SEABLUE)
            cv.fill(x + 90, 806, 30, 24, NAVY)
            cv.fill(x + 150, 812, 18, 18, NAVY)
            cv.fill(x + 40, 856, 236, 6, DARKGREY)
            mx, my = x + 278, 824
            cv.disc(mx, my, 12, INK)
            for dx, dy in ((0, -16), (12, -12), (16, 0), (12, 12),
                           (0, 16), (-12, 12), (-16, 0), (-12, -12)):
                cv.line(mx, my, mx + dx, my + dy, INK)
        cv.paragraph(x, 888, headline, 316, 2, INK)


if __name__ == '__main__':
    raise SystemExit(main())
