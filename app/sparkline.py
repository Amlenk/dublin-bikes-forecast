"""Server-rendered inline-SVG sparkline of recent bike availability.

Pure string builder — no I/O. Follows the page's minimal style: single
series in the page accent blue (#2b6cb0, contrast-validated on white),
y fixed to [0, capacity] so fullness/emptiness reads honestly, x is a
true time scale (gaps in the pipeline show as gaps in pace, not hidden
by index spacing). Native <title> tooltips give per-point values with
zero JavaScript.
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

DUBLIN = ZoneInfo("Europe/Dublin")

WIDTH, HEIGHT = 320, 84
PAD_LEFT, PAD_RIGHT, PAD_TOP, PAD_BOTTOM = 26, 8, 8, 16
LINE = "#2b6cb0"
MUTED = "#718096"
GRID = "#e2e8f0"


def build_sparkline(points: list, capacity: int) -> str | None:
    """points: [(ts UTC-aware, bikes), ...] sorted by ts. None if the
    data cannot make an honest line (fewer than 2 points)."""
    if len(points) < 2 or capacity <= 0:
        return None
    t0, t1 = points[0][0], points[-1][0]
    span = (t1 - t0).total_seconds()
    if span <= 0:
        return None
    x0, x1 = PAD_LEFT, WIDTH - PAD_RIGHT
    y0, y1 = HEIGHT - PAD_BOTTOM, PAD_TOP  # y grows downward in SVG

    def x(ts: datetime) -> float:
        return x0 + (x1 - x0) * (ts - t0).total_seconds() / span

    def y(bikes: int) -> float:
        return y0 + (y1 - y0) * min(bikes, capacity) / capacity

    coords = [(x(ts), y(b)) for ts, b in points]
    line_pts = " ".join(f"{cx:.1f},{cy:.1f}" for cx, cy in coords)
    area_pts = f"{coords[0][0]:.1f},{y0} {line_pts} {coords[-1][0]:.1f},{y0}"

    hovers = "".join(
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="7" fill="transparent">'
        f"<title>{ts.astimezone(DUBLIN):%H:%M} — {b} bikes</title></circle>"
        for (cx, cy), (ts, b) in zip(coords, points)
    )
    last_x, last_y = coords[-1]
    return (
        f'<svg viewBox="0 0 {WIDTH} {HEIGHT}" role="img" '
        f'aria-label="Bikes available over the last 24 hours">'
        f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="{GRID}" stroke-width="1"/>'
        f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="{GRID}" '
        f'stroke-width="1" stroke-dasharray="2,3"/>'
        f'<text x="{x0 - 4}" y="{y0 + 3}" text-anchor="end" font-size="9" fill="{MUTED}">0</text>'
        f'<text x="{x0 - 4}" y="{y1 + 3}" text-anchor="end" font-size="9" fill="{MUTED}">{capacity}</text>'
        f'<text x="{x0}" y="{HEIGHT - 3}" font-size="9" fill="{MUTED}">'
        f"{t0.astimezone(DUBLIN):%H:%M}</text>"
        f'<text x="{x1}" y="{HEIGHT - 3}" text-anchor="end" font-size="9" fill="{MUTED}">'
        f"{t1.astimezone(DUBLIN):%H:%M}</text>"
        f'<polygon points="{area_pts}" fill="{LINE}" opacity="0.12"/>'
        f'<polyline points="{line_pts}" fill="none" stroke="{LINE}" stroke-width="2" '
        f'stroke-linejoin="round" stroke-linecap="round"/>'
        f'<circle cx="{last_x:.1f}" cy="{last_y:.1f}" r="4" fill="{LINE}"/>'
        f"{hovers}</svg>"
    )
