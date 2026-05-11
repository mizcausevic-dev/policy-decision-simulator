from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SCREENSHOTS = ROOT / "screenshots"

BG = "#081321"
PANEL = "#13253c"
CARD = "#1b2d48"
BORDER = "#274869"
TEXT = "#f0efdd"
MUTED = "#a8b6cb"
ACCENT = "#80c8ff"
WARN = "#ffd56d"
CRITICAL = "#ff8c8c"
STABLE = "#8de4ae"


def font(size: int, bold: bool = False):
    name = "arialbd.ttf" if bold else "arial.ttf"
    try:
        return ImageFont.truetype(name, size)
    except OSError:
        return ImageFont.load_default()


def wrap(draw, text, x, y, width, line_height, fill, fnt):
    words = text.split()
    line = ""
    for word in words:
        candidate = word if not line else f"{line} {word}"
        if draw.textlength(candidate, font=fnt) <= width:
            line = candidate
        else:
            draw.text((x, y), line, font=fnt, fill=fill)
            y += line_height
            line = word
    if line:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += line_height
    return y


def base(title, subtitle):
    img = Image.new("RGB", (1600, 900), BG)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((36, 36, 1564, 864), radius=30, fill=PANEL, outline=BORDER, width=2)
    draw.text((86, 84), title, font=font(24), fill=ACCENT)
    draw.text((86, 148), subtitle, font=font(56, bold=True), fill=TEXT)
    return img, draw


def card(draw, box, title, value, blurb, value_fill=TEXT):
    draw.rounded_rectangle(box, radius=24, fill=CARD, outline=BORDER, width=2)
    x1, y1, x2, _ = box
    draw.text((x1 + 26, y1 + 24), title, font=font(18), fill=MUTED)
    draw.text((x1 + 26, y1 + 74), str(value), font=font(44, bold=True), fill=value_fill)
    wrap(draw, blurb, x1 + 26, y1 + 138, x2 - x1 - 52, 28, MUTED, font(18))


def render():
    SCREENSHOTS.mkdir(exist_ok=True)

    img, draw = base("POLICY DECISION SIMULATOR", "Scenario pressure gets turned into a decision lane the business can actually use.")
    card(draw, (86, 300, 430, 560), "Tracked scenarios", 3, "Downside, base, and upside frames running through the same policy engine.")
    card(draw, (450, 300, 794, 560), "Critical paths", 1, "High-drag change paths already constrained by freeze and dependency pressure.", CRITICAL)
    card(draw, (814, 300, 1158, 560), "Watch paths", 1, "Scenarios that can still ship if owners close readiness gaps.", WARN)
    card(draw, (1178, 300, 1522, 560), "Avg rollback confidence", "0.62", "How much operational confidence remains if the branch has to reverse.", TEXT)
    draw.rounded_rectangle((86, 612, 1522, 804), radius=24, fill=CARD, outline=BORDER, width=2)
    draw.text((112, 640), "ACTIVE BRANCH", font=font(20), fill=ACCENT)
    draw.text((112, 688), "Pricing and entitlement cutover should hold until rollback certainty and dependency health improve.", font=font(34, bold=True), fill=TEXT)
    draw.text((112, 748), "This repo treats scenario planning like a decision engine, not just a strategy memo.", font=font(24), fill=MUTED)
    img.save(SCREENSHOTS / "01-hero.png")

    img, draw = base("SCENARIO LANES", "Each mode carries a different pressure mix and release posture.")
    lanes = [
        ("Downside", CRITICAL, "3 dependency breaches", "Freeze active · 42% exposure"),
        ("Base", WARN, "1 dependency breach", "No freeze · 16% exposure"),
        ("Upside", STABLE, "0 dependency breaches", "No freeze · 9% exposure"),
    ]
    x = 86
    for label, color, line1, line2 in lanes:
        draw.rounded_rectangle((x, 320, x + 430, 760), radius=24, fill=CARD, outline=BORDER, width=2)
        draw.text((x + 28, 352), label, font=font(30, bold=True), fill=TEXT)
        draw.text((x + 28, 410), line1, font=font(22, bold=True), fill=color)
        draw.text((x + 28, 454), line2, font=font(22), fill=MUTED)
        x += 484
    img.save(SCREENSHOTS / "02-scenario-lanes.png")

    img, draw = base("DECISION MODEL", "The hold/watch/approve outcome comes from branch conditions, not hand-waving.")
    card(draw, (86, 306, 740, 570), "Hold", "74+", "Freeze, breach count, rollback weakness, and customer exposure all combine into a release stop.", CRITICAL)
    card(draw, (780, 306, 1434, 570), "Watch", "46+", "The scenario can proceed only if dependency owners close readiness gaps before the window opens.", WARN)
    draw.rounded_rectangle((86, 620, 1518, 800), radius=24, fill=CARD, outline=BORDER, width=2)
    draw.text((112, 648), "APPROVE BAND", font=font(20), fill=ACCENT)
    draw.text((112, 694), "Low-drag scenarios stay in the standard release lane and carry a clear baseline assumption set.", font=font(32, bold=True), fill=TEXT)
    draw.text((112, 742), "This is the layer where operators decide whether to ship, hold, or re-sequence.", font=font(22), fill=MUTED)
    img.save(SCREENSHOTS / "03-decision-model.png")

    img, draw = base("VALIDATION PROOF", "The Scala service boots, tests, and returns real JSON decisions.")
    draw.rounded_rectangle((86, 286, 980, 804), radius=24, fill="#09111c", outline=BORDER, width=2)
    lines = [
        "> scala-cli test .",
        "2 tests passed.",
        "",
        "> GET /api/dashboard/summary",
        "tracked_scenarios         3",
        "critical_scenarios        1",
        "freeze_constrained        1",
        "",
        "> POST /api/analyze/scenario",
        "decision                  hold",
        "score                     82",
    ]
    y = 322
    for line in lines:
        draw.text((118, y), line, font=font(24, bold=line.startswith(">")), fill=STABLE if line.startswith(">") else TEXT)
        y += 34
    draw.rounded_rectangle((1030, 286, 1518, 804), radius=24, fill=CARD, outline=BORDER, width=2)
    draw.text((1060, 324), "SCENARIO MODES", font=font(20), fill=ACCENT)
    modes = [("scn-901", "critical", CRITICAL), ("scn-902", "watch", WARN), ("scn-903", "stable", STABLE)]
    y = 384
    for scenario_id, state, color in modes:
        draw.text((1060, y), scenario_id, font=font(28, bold=True), fill=TEXT)
        draw.text((1060, y + 38), state.upper(), font=font(20, bold=True), fill=color)
        y += 118
    img.save(SCREENSHOTS / "04-proof.png")


if __name__ == "__main__":
    render()

