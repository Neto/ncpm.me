#!/usr/bin/env python3
"""Spoon Software logo: a capital S in the neon line style of the Spin and Grabb icons.

Takes the S outline from Helvetica Neue Bold, rounds its sharp corners, and places it
on the 1024 point icon canvas (the dark squircle is 824 points wide, inset 100).

Writes:
  design/logo-s.path       SVG path data, in squircle coordinates (0 to 824)
  design/MakeLogo.swift    SwiftUI renderer for the static PNG (run it with swift)
  design/spoon-logo-outline.svg  one colour outline, for print and documents

Needs fontTools:  python3 -m pip install fonttools
"""
import math
import pathlib

from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTCollection

FONT = "/System/Library/Fonts/HelveticaNeue.ttc"
FACE = 1                # Helvetica Neue Bold
CORNER_RADIUS = 42      # font units; the S terminals are about 152 units thick
CAP = 492               # height of the S on the 1024 canvas
CANVAS, INSET = 1024, 100

here = pathlib.Path(__file__).resolve().parent


# ---------- outline as a list of segments: ("L", p0, p1) or ("Q", p0, c, p1) ----------

def glyph_segments():
    font = TTCollection(FONT).fonts[FACE]
    pen = RecordingPen()
    font.getGlyphSet()[font.getBestCmap()[ord("S")]].draw(pen)
    segs, cur, start = [], None, None
    for op, args in pen.value:
        if op == "moveTo":
            cur = start = args[0]
        elif op == "lineTo":
            segs.append(("L", cur, args[0]))
            cur = args[0]
        elif op == "qCurveTo":
            *offs, end = args
            for i, c in enumerate(offs):
                nxt = end if i == len(offs) - 1 else ((c[0] + offs[i + 1][0]) / 2, (c[1] + offs[i + 1][1]) / 2)
                segs.append(("Q", cur, c, nxt))
                cur = nxt
        elif op == "closePath":
            if cur != start:
                segs.append(("L", cur, start))
    return segs


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def split(seg, t):
    """Split a segment at t; returns (first, second)."""
    if seg[0] == "L":
        _, a, b = seg
        m = lerp(a, b, t)
        return ("L", a, m), ("L", m, b)
    _, a, c, b = seg
    ac, cb = lerp(a, c, t), lerp(c, b, t)
    m = lerp(ac, cb, t)
    return ("Q", a, ac, m), ("Q", m, cb, b)


def point(seg, t):
    return split(seg, t)[0][-1]


def t_at_distance(seg, d, from_end):
    """Parameter where the chord from the chosen end point is d long."""
    anchor = seg[-1] if from_end else seg[1]
    lo, hi = 0.0, 1.0
    for _ in range(50):
        mid = (lo + hi) / 2
        t = 1 - mid if from_end else mid
        if math.dist(anchor, point(seg, t)) < d:
            lo = mid
        else:
            hi = mid
    return 1 - lo if from_end else lo


def direction(seg, at_end):
    if seg[0] == "L":
        a, b = seg[1], seg[2]
    else:
        a, b = (seg[2], seg[3]) if at_end else (seg[1], seg[2])
    n = math.dist(a, b)
    return ((b[0] - a[0]) / n, (b[1] - a[1]) / n)


def round_corners(segs, r):
    """Replace each sharp corner with a quadratic fillet whose control point is the corner."""
    n = len(segs)
    sharp = []
    for i in range(n):
        u, v = direction(segs[i], True), direction(segs[(i + 1) % n], False)
        if u[0] * v[0] + u[1] * v[1] < math.cos(math.radians(25)):
            sharp.append(i)
    out = list(segs)
    for i in sharp:
        j = (i + 1) % n
        before, _ = split(out[i], t_at_distance(out[i], r, from_end=True))
        _, after = split(out[j], t_at_distance(out[j], r, from_end=False))
        out[i], out[j] = before, after
    result = []
    for i, seg in enumerate(out):
        result.append(seg)
        if i in sharp:
            nxt = out[(i + 1) % n]
            result.append(("Q", seg[-1], segs[i][-1], nxt[1]))
    return result, len(sharp)


# ---------- placement and output ----------

segs, corners = round_corners(glyph_segments(), CORNER_RADIUS)
xs = [p[0] for s in segs for p in s[1:]]
ys = [p[1] for s in segs for p in s[1:]]
scale = CAP / (max(ys) - min(ys))
cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2


def place(p, offset):
    """Font units to canvas points: flip y, scale, centre on the canvas."""
    return (round(CANVAS / 2 + (p[0] - cx) * scale - offset, 2),
            round(CANVAS / 2 - (p[1] - cy) * scale - offset, 2))


def svg_path(offset):
    d = [f"M{place(segs[0][1], offset)[0]} {place(segs[0][1], offset)[1]}"]
    for s in segs:
        pts = [place(p, offset) for p in s[2:]]
        d.append(("L" if s[0] == "L" else "Q") + " ".join(f"{x} {y}" for x, y in pts))
    return "".join(d) + "Z"


squircle_path = svg_path(INSET)
(here / "logo-s.path").write_text(squircle_path + "\n")

(here / "spoon-logo-outline.svg").write_text(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 824 824" width="824" height="824">\n'
    '<rect width="824" height="824" rx="185" fill="#111"/>\n'
    f'<path d="{squircle_path}" fill="none" stroke="#fff" stroke-width="5" stroke-linejoin="round"/>\n'
    '</svg>\n')

swift_lines = []
for i, s in enumerate(segs):
    if i == 0:
        x, y = place(s[1], 0)
        swift_lines.append(f"        p.move(to: CGPoint(x: {x}, y: {y}))")
    if s[0] == "L":
        x, y = place(s[2], 0)
        swift_lines.append(f"        p.addLine(to: CGPoint(x: {x}, y: {y}))")
    else:
        (qx, qy), (x, y) = place(s[2], 0), place(s[3], 0)
        swift_lines.append(f"        p.addQuadCurve(to: CGPoint(x: {x}, y: {y}), control: CGPoint(x: {qx}, y: {qy}))")
swift_lines.append("        p.closeSubpath()")

swift = (here / "MakeLogo.swift.in").read_text().replace("// PATH", "\n".join(swift_lines))
(here / "MakeLogo.swift").write_text(swift)
print(f"{len(segs)} segments, {corners} corners rounded, scale {scale:.3f}")
