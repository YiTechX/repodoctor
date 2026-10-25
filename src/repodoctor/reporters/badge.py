from __future__ import annotations

from xml.sax.saxutils import escape

from ..scoring import Report
from .base import RenderOptions, reporter

LABEL = "repo health"
CHAR_WIDTH = 6.6
PADDING = 12
COLOR_STEPS = ((90, "#4c1"), (80, "#97ca00"), (70, "#dfb317"), (60, "#fe7d37"))
FALLBACK_COLOR = "#e05d44"


def badge_color(score: int) -> str:
    for threshold, color in COLOR_STEPS:
        if score >= threshold:
            return color
    return FALLBACK_COLOR


def make_badge(label: str, value: str, color: str) -> str:
    left = round(len(label) * CHAR_WIDTH) + PADDING
    right = round(len(value) * CHAR_WIDTH) + PADDING
    total = left + right
    text = escape(f"{label}: {value}")
    label_x = left / 2
    value_x = left + right / 2
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total}" height="20" '
        f'role="img" aria-label="{text}">'
        f"<title>{text}</title>"
        '<linearGradient id="s" x2="0" y2="100%">'
        '<stop offset="0" stop-color="#bbb" stop-opacity=".1"/>'
        '<stop offset="1" stop-opacity=".1"/></linearGradient>'
        f'<clipPath id="r"><rect width="{total}" height="20" rx="3" fill="#fff"/></clipPath>'
        '<g clip-path="url(#r)">'
        f'<rect width="{left}" height="20" fill="#555"/>'
        f'<rect x="{left}" width="{right}" height="20" fill="{color}"/>'
        f'<rect width="{total}" height="20" fill="url(#s)"/></g>'
        '<g fill="#fff" text-anchor="middle" '
        'font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11">'
        f'<text x="{label_x}" y="14">{escape(label)}</text>'
        f'<text x="{value_x}" y="14">{escape(value)}</text></g></svg>\n'
    )


@reporter("badge")
def render_badge(report: Report, options: RenderOptions) -> str:
    return make_badge(LABEL, f"{report.score}/100", badge_color(report.score))
