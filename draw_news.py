#!/usr/bin/env python3
"""Draw the front page of "The Thursday Globe" for 26 November 2026.

Pure Python standard-library renderer: it builds a 1024x1024 RGB framebuffer
in memory and writes a PNG using only zlib + struct. No PIL, no numpy, no
third-party packages.
"""

import os
import struct
import zlib

W = 1024
H = 1024

# ----------------------------------------------------------------------------
# Palette
# ----------------------------------------------------------------------------
PAPER = (250, 246, 236)      # warm newsprint background
PANEL = (247, 242, 231)      # slightly deeper panel fill
INK = (22, 20, 18)           # near-black headline ink
INK_SOFT = (74, 66, 58)      # caption grey-brown
RULE = (44, 38, 32)          # hairline rules
WHITE = (251, 251, 249)

TAG_HUAWEI = (150, 34, 34)   # dark red
TAG_ENERGY = (172, 62, 22)   # burnt orange for the energy lead
TAG_MARKET = (28, 82, 138)   # blue
TAG_NATO = (22, 96, 96)      # teal
TAG_POLAND = (190, 44, 62)   # crimson
TAG_KYIV = (46, 74, 150)     # steel blue
TAG_USA = (28, 56, 118)      # navy
TAG_INDIA = (206, 92, 20)    # saffron

STEEL = (122, 126, 132)
STEEL_DARK = (78, 82, 92)
SMOKE_DARK = (66, 66, 72)
SMOKE_MID = (108, 108, 116)
SMOKE_LIGHT = (152, 152, 158)
FLAME = (226, 116, 28)
FLAME_CORE = (250, 198, 60)
WOOD = (142, 98, 44)
WOOD_DARK = (96, 62, 30)
BRASS = (158, 122, 58)
RED_FLAG = (200, 40, 46)
GREEN_IN = (18, 128, 60)
SAFFRON_IN = (255, 122, 28)
CHAKRA = (20, 60, 140)

# ----------------------------------------------------------------------------
# Framebuffer
# ----------------------------------------------------------------------------
img = bytearray(bytes(PAPER) * (W * H))


def set_px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        img[i] = c[0]
        img[i + 1] = c[1]
        img[i + 2] = c[2]


def fill_rect(x0, y0, x1, y1, c):
    x0 = max(0, int(x0))
    y0 = max(0, int(y0))
    x1 = min(W, int(x1))
    y1 = min(H, int(y1))
    if x0 >= x1 or y0 >= y1:
        return
    row = bytes(c) * (x1 - x0)
    for y in range(y0, y1):
        base = (y * W + x0) * 3
        img[base:base + len(row)] = row


def draw_rect(x0, y0, x1, y1, c, t=1):
    fill_rect(x0, y0, x1, y0 + t, c)
    fill_rect(x0, y1 - t, x1, y1, c)
    fill_rect(x0, y0, x0 + t, y1, c)
    fill_rect(x1 - t, y0, x1, y1, c)


def hline(x0, x1, y, c, t=1):
    fill_rect(x0, y, x1, y + t, c)


def vline(x, y0, y1, c, t=1):
    fill_rect(x, y0, x + t, y1, c)


def fill_circle(cx, cy, r, c):
    r2 = r * r
    x0 = max(0, int(cx - r))
    x1 = min(W - 1, int(cx + r))
    y0 = max(0, int(cy - r))
    y1 = min(H - 1, int(cy + r))
    for y in range(y0, y1 + 1):
        dy = y - cy
        dy2 = dy * dy
        for x in range(x0, x1 + 1):
            dx = x - cx
            if dx * dx + dy2 <= r2:
                set_px(x, y, c)


def draw_circle(cx, cy, r, c, t=1):
    for y in range(max(0, int(cy - r)), min(H, int(cy + r) + 1)):
        for x in range(max(0, int(cx - r)), min(W, int(cx + r) + 1)):
            d = (x - cx) * (x - cx) + (y - cy) * (y - cy)
            if (r - t) * (r - t) <= d <= r * r:
                set_px(x, y, c)


def fill_triangle(ax, ay, bx, by, cx, cy, c):
    minx = max(0, int(min(ax, bx, cx)))
    maxx = min(W - 1, int(max(ax, bx, cx)))
    miny = max(0, int(min(ay, by, cy)))
    maxy = min(H - 1, int(max(ay, by, cy)))
    for y in range(miny, maxy + 1):
        for x in range(minx, maxx + 1):
            d1 = (x - bx) * (ay - by) - (ax - bx) * (y - by)
            d2 = (x - cx) * (by - cy) - (bx - cx) * (y - cy)
            d3 = (x - ax) * (cy - ay) - (cx - ax) * (y - ay)
            neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
            pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
            if not (neg and pos):
                set_px(x, y, c)


# ----------------------------------------------------------------------------
# 5x7 bitmap font (row strings of '#', width 5, height 7)
# ----------------------------------------------------------------------------
FONT = {
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    'a': (".....", ".....", ".###.", "....#", ".####", "#...#", ".####"),
    'b': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    'c': (".....", ".....", ".###.", "#....", "#....", "#....", ".###."),
    'd': ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    'e': (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    'f': ("..##.", ".#..#", ".#...", "####.", ".#...", ".#...", ".#..."),
    'g': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    'h': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'i': ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."),
    'j': ("...#.", ".....", "..##.", "...#.", "...#.", "...#.", ".##.."),
    'k': ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    'l': (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'm': (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    'n': (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'o': (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    'p': (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
    'q': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    'r': (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    's': (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    't': (".#...", ".#...", "####.", ".#...", ".#...", ".#..#", "..##."),
    'u': (".....", ".....", "#...#", "#...#", "#...#", "#...#", ".####"),
    'v': (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'w': (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    'x': (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    'y': (".....", ".....", "#...#", "#...#", "#...#", ".####", "....#"),
    'z': (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    '0': ("..###", ".#..#", ".#..#", ".#..#", ".#..#", ".#..#", "..###"),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': (".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."),
    '4': ("#...#", "#...#", "#...#", "#####", "....#", "....#", "....#"),
    '5': ("#####", "#....", "#....", "####.", "....#", "#...#", ".###."),
    '6': ("..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", "..#..", "..#..", ".#..."),
    ':': (".....", ".....", ".##..", ".##..", ".....", ".##..", ".##.."),
    ';': (".....", ".....", ".##..", ".##..", ".....", ".##..", ".#..."),
    '-': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    '—': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    '%': ("#...#", "....#", "...#.", "..#..", ".#...", "....#", "#...#"),
    '+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    '$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '&': ("..##.", ".#..#", ".#.#.", "..#..", ".#.#.", "#..#.", ".##.#"),
    '~': (".....", ".....", ".....", ".#.#.", "#.#.#", ".....", "....."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
}


def text_w(s, scale):
    if not s:
        return 0
    return len(s) * 6 * scale - scale


def text_h(scale):
    return 7 * scale


def draw_text(s, x, y, scale, c):
    cx = int(x)
    for ch in s:
        glyph = FONT.get(ch, FONT['?'])
        for gy, row in enumerate(glyph):
            ry = y + gy * scale
            for gx, bit in enumerate(row):
                if bit == '#':
                    fill_rect(cx + gx * scale, ry, cx + (gx + 1) * scale, ry + scale, c)
        cx += 6 * scale


def draw_text_center(s, y, scale, c):
    draw_text(s, (W - text_w(s, scale)) // 2, y, scale, c)


def wrap_text(s, scale, max_px):
    words = s.split(' ')
    lines = []
    cur = ''
    for w in words:
        trial = w if not cur else cur + ' ' + w
        if text_w(trial, scale) <= max_px:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ----------------------------------------------------------------------------
# Small motifs (each drawn around a centre point)
# ----------------------------------------------------------------------------
def motif_scales(cx, cy):
    fill_rect(cx - 2, cy - 20, cx + 2, cy + 18, INK)
    fill_rect(cx - 26, cy - 18, cx + 26, cy - 13, INK)
    fill_triangle(cx - 30, cy - 9, cx - 14, cy - 9, cx - 22, cy + 13, BRASS)
    fill_triangle(cx + 14, cy - 9, cx + 30, cy - 9, cx + 22, cy + 13, BRASS)
    vline(cx - 28, cy - 13, cy - 9, INK)
    vline(cx - 16, cy - 13, cy - 9, INK)
    vline(cx + 16, cy - 13, cy - 9, INK)
    vline(cx + 28, cy - 13, cy - 9, INK)


def motif_down_arrow(cx, cy):
    c = RED_FLAG
    fill_rect(cx - 5, cy - 22, cx + 5, cy + 4, c)
    fill_triangle(cx - 18, cy - 2, cx + 18, cy - 2, cx, cy + 22, c)


def motif_compass(cx, cy):
    c = TAG_NATO
    draw_circle(cx, cy, 24, c, 2)
    fill_triangle(cx, cy - 20, cx - 6, cy - 2, cx + 6, cy - 2, c)
    fill_triangle(cx, cy + 20, cx - 6, cy + 2, cx + 6, cy + 2, c)
    fill_triangle(cx - 20, cy, cx - 2, cy - 6, cx - 2, cy + 6, c)
    fill_triangle(cx + 20, cy, cx + 2, cy - 6, cx + 2, cy + 6, c)


def motif_flag_pl(cx, cy):
    fill_rect(cx - 26, cy - 20, cx - 22, cy + 22, INK)
    fill_rect(cx - 22, cy - 18, cx + 18, cy - 5, (242, 242, 242))
    fill_rect(cx - 22, cy - 5, cx + 18, cy + 9, RED_FLAG)
    draw_rect(cx - 22, cy - 18, cx + 18, cy + 9, INK, 1)


def motif_missile(cx, cy):
    c = TAG_KYIV
    fill_rect(cx - 20, cy - 5, cx + 10, cy + 5, c)
    fill_triangle(cx + 10, cy - 5, cx + 10, cy + 5, cx + 25, cy, c)
    fill_triangle(cx - 20, cy - 5, cx - 20, cy + 5, cx - 31, cy + 15, c)
    fill_triangle(cx - 20, cy - 5, cx - 20, cy + 5, cx - 31, cy - 15, c)
    fill_triangle(cx - 20, cy - 3, cx - 20, cy + 3, cx - 33, cy, FLAME)


def motif_flag_us(cx, cy):
    fill_rect(cx - 26, cy - 20, cx - 22, cy + 22, INK)
    fill_rect(cx - 22, cy - 18, cx + 18, cy + 10, (242, 242, 242))
    for i in range(4):
        fill_rect(cx - 22, cy - 18 + i * 7, cx + 18, cy - 16 + i * 7, RED_FLAG)
    fill_rect(cx - 22, cy - 18, cx - 6, cy - 4, (30, 56, 130))
    for sx in range(cx - 20, cx - 7, 6):
        for sy in range(cy - 16, cy - 5, 5):
            fill_rect(sx, sy, sx + 2, sy + 2, (242, 242, 242))
    draw_rect(cx - 22, cy - 18, cx + 18, cy + 10, INK, 1)


def motif_flag_in(cx, cy):
    fill_rect(cx - 26, cy - 20, cx - 22, cy + 22, INK)
    fill_rect(cx - 22, cy - 16, cx + 18, cy - 8, SAFFRON_IN)
    fill_rect(cx - 22, cy - 8, cx + 18, cy, (250, 250, 250))
    fill_rect(cx - 22, cy, cx + 18, cy + 8, GREEN_IN)
    fill_circle(cx - 2, cy - 4, 3, CHAKRA)
    draw_rect(cx - 22, cy - 16, cx + 18, cy + 8, INK, 1)


# ----------------------------------------------------------------------------
# The lead motif: a burning refinery with a smoke plume
# ----------------------------------------------------------------------------
def draw_refinery(x0, y0, x1, y1):
    gy = y1 - 16                      # ground line
    fill_rect(x0, gy, x1, y1, (62, 58, 54))
    # storage tank 1
    fill_rect(x0 + 8, gy - 48, x0 + 52, gy, STEEL)
    draw_rect(x0 + 8, gy - 48, x0 + 52, gy, INK, 1)
    fill_rect(x0 + 12, gy - 56, x0 + 48, gy - 48, STEEL_DARK)
    # pipe to column
    fill_rect(x0 + 52, gy - 62, x0 + 66, gy - 58, STEEL_DARK)
    # distillation column
    fill_rect(x0 + 66, gy - 84, x0 + 86, gy, STEEL_DARK)
    draw_rect(x0 + 66, gy - 84, x0 + 86, gy, INK, 1)
    fill_rect(x0 + 70, gy - 90, x0 + 82, gy - 84, STEEL)
    # storage tank 2
    fill_rect(x0 + 96, gy - 40, x0 + 138, gy, STEEL)
    draw_rect(x0 + 96, gy - 40, x0 + 138, gy, INK, 1)
    fill_rect(x0 + 100, gy - 46, x0 + 134, gy - 40, STEEL_DARK)
    # connecting pipe
    fill_rect(x0 + 86, gy - 52, x0 + 96, gy - 48, STEEL_DARK)
    # flare stack
    fx = x0 + 172
    fill_rect(fx, gy - 118, fx + 9, gy, STEEL_DARK)
    draw_rect(fx, gy - 118, fx + 9, gy, INK, 1)
    # flame
    fill_triangle(fx - 8, gy - 118, fx + 17, gy - 118, fx + 4, gy - 152, FLAME)
    fill_triangle(fx + 1, gy - 118, fx + 9, gy - 118, fx + 4, gy - 144, FLAME_CORE)
    # smoke plume rising and drifting right
    smoke = [
        (fx + 4, gy - 124, 13, SMOKE_DARK),
        (fx + 12, gy - 140, 18, SMOKE_DARK),
        (fx + 22, gy - 158, 22, SMOKE_MID),
        (fx + 34, gy - 176, 24, SMOKE_MID),
        (fx + 48, gy - 188, 22, SMOKE_LIGHT),
        (fx + 60, gy - 194, 16, SMOKE_LIGHT),
    ]
    for (sx, sy, r, c) in smoke:
        fill_circle(sx, sy, r, c)


# ----------------------------------------------------------------------------
# Layout helpers
# ----------------------------------------------------------------------------
M = 26


def draw_tag(x, y, label, color):
    tw = text_w(label, 2) + 10
    fill_rect(x, y, x + tw, y + 18, color)
    draw_text(label, x + 5, y + 3, 2, WHITE)


def draw_panel(px, py, pw, ph, tag, tag_color, headline, caption, motif, motif_x, motif_y):
    fill_rect(px, py, px + pw, py + ph, PANEL)
    draw_rect(px, py, px + pw, py + ph, INK, 2)
    draw_tag(px + 10, py + 10, tag, tag_color)
    draw_text(headline, px + 12, py + 34, 3, INK)
    cap_w = pw - 12 - 92 - 12
    lines = wrap_text(caption, 2, cap_w)
    ty = py + 62
    for ln in lines[:3]:
        draw_text(ln, px + 12, ty, 2, INK_SOFT)
        ty += 16
    motif(motif_x, motif_y)


# ----------------------------------------------------------------------------
# Compose the page
# ----------------------------------------------------------------------------
def compose():
    # --- Masthead ----------------------------------------------------------
    draw_text_center("THE THURSDAY GLOBE", 34, 8, INK)
    # --- Date line ---------------------------------------------------------
    draw_text_center("Thursday, 26 November 2026", 96, 3, INK)
    # --- Dateline rules ----------------------------------------------------
    hline(M, W - M, 126, RULE, 2)
    hline(M, W - M, 132, RULE, 2)

    # --- Lead story --------------------------------------------------------
    lx0, ly0, lx1, ly1 = M, 148, W - M, 396
    fill_rect(lx0, ly0, lx1, ly1, PANEL)
    draw_rect(lx0, ly0, lx1, ly1, INK, 3)
    draw_tag(lx0 + 14, ly0 + 14, "MIDDLE EAST", TAG_ENERGY)
    draw_text("HOUTHIS STRIKE RAS TANURA", lx0 + 16, ly0 + 40, 4, INK)
    summary = "Yemen's Houthis hit Saudi Arabia's largest oil refinery; Brent crude jumps 2% to $93.60."
    sy = ly0 + 82
    for ln in wrap_text(summary, 2, 560)[:3]:
        draw_text(ln, lx0 + 16, sy, 2, INK_SOFT)
        sy += 17
    # small data strip under the summary (kept inside the text column)
    draw_text("Ras Tanura 550,000 b/d - smoke over 600 sq km", lx0 + 16, ly0 + 140, 2, (96, 80, 64))
    draw_refinery(lx0 + 640, ly0 + 30, lx1 - 24, ly1 - 16)

    # --- Grid of smaller stories ------------------------------------------
    gx0, gy0 = M, 410
    col_gap = 18
    row_gap = 14
    col_w = (W - 2 * M - col_gap) // 2
    rows = 4
    row_h = ((H - M - 12) - gy0 - row_gap * (rows - 1)) // rows

    panels = [
        ("HUAWEI", TAG_HUAWEI, "HUAWEI CONVICTED",
         "Brooklyn jury: guilty on 10 of 12 counts; appeal planned.",
         motif_scales),
        ("MARKETS", TAG_MARKET, "AI STOCKS ROUT",
         "Nvidia -7.3%, Micron -10%, Nasdaq -4% before Thanksgiving.",
         motif_down_arrow),
        ("NATO", TAG_NATO, "RUTTE MEETS TRUMP",
         "Ukraine 'doing exceptionally well'; 50,000 Russian losses in Oct.",
         motif_compass),
        ("POLAND", TAG_POLAND, "POLAND WANTS US TROOPS",
         "Two Russian airspace incursions in four days.",
         motif_flag_pl),
        ("KYIV", TAG_KYIV, "SAVASLEYKA STRIKE",
         "Five Russian aircraft damaged; Kyiv asks for 40 more F-16s.",
         motif_missile),
        ("USA", TAG_USA, "US GDP UP 4.3%",
         "Fastest growth in 3 years; turkey pardon for Freedom and Feathers.",
         motif_flag_us),
    ]
    # rows 0..2: two panels each; row 3: India full width
    for r in range(3):
        py = gy0 + r * (row_h + row_gap)
        for c in range(2):
            px = gx0 + c * (col_w + col_gap)
            tag, tcol, head, cap, mfn = panels[r * 2 + c]
            mx = px + col_w - 66
            my = py + row_h // 2 + 2
            draw_panel(px, py, col_w, row_h, tag, tcol, head, cap, mfn, mx, my)

    # India full-width panel
    ipy = gy0 + 3 * (row_h + row_gap)
    iw = W - 2 * M
    draw_panel(gx0, ipy, iw, row_h, "INDIA", TAG_INDIA, "INDIA MARKS 26/11",
               "18 years since Mumbai attacks; Rs 15,000 crore aid for Nepal.",
               motif_flag_in, gx0 + iw - 76, ipy + row_h // 2 + 2)

    # --- Footer ------------------------------------------------------------
    fy = H - M - 4
    hline(M, W - M, fy - 18, RULE, 1)
    draw_text_center("Thanksgiving Day in the United States — markets closed", fy - 12, 2, INK_SOFT)


# ----------------------------------------------------------------------------
# PNG writer
# ----------------------------------------------------------------------------
def write_png(path):
    stride = W * 3
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter type: None
        raw += img[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = sig + chunk(b'IHDR', ihdr) + chunk(b'IDAT', comp) + chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)


if __name__ == '__main__':
    compose()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'entry.png')
    write_png(out)
    print('wrote', out, os.path.getsize(out), 'bytes')
