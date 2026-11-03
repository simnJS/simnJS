"""Shared look for the generated SVG cards."""
from xml.sax.saxutils import escape

BG, BORDER, CHIP = "#101016", "#26263A", "#1B1B28"
TITLE, ICON, TEXT, MUTED = "#F5A3C7", "#C9A3F5", "#DCDCE4", "#8A8A9A"
PALETTE = ["#F5A3C7", "#C9A3F5", "#8FB4F5", "#9FD8A4", "#F5D08F", "#F5A38F", "#A3E5F5", "#DCDCE4"]
FONT = "'JetBrains Mono','SFMono-Regular',Consolas,'Liberation Mono',monospace"


def svg(width, height, label, body):
    return (
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{escape(label)}">'
        f"<style>text{{font-family:{FONT}}}</style>"
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>'
        f"{body}</svg>"
    )


def titled_card(width, height, title, body):
    heading = f'<text x="25" y="35" font-size="16" font-weight="700" fill="{TITLE}">{escape(title)}</text>'
    return svg(width, height, title, heading + body)
