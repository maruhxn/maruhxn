#!/usr/bin/env python3
"""README의 Skills 카드 SVG 생성기.

SKILLS 딕셔너리만 수정한 뒤 실행하면 assets/skills-light.svg, assets/skills-dark.svg 가 갱신된다.

    python3 scripts/gen_skills_svg.py
"""
from pathlib import Path
from xml.sax.saxutils import escape

SKILLS = {
    "Backend": ["Kotlin", "Java", "Spring Boot", "Spring Security",
                "Spring Batch", "JPA / QueryDSL", "Resilience4j"],
    "Database": ["MySQL", "PostgreSQL", "Redis"],
    "DevOps": ["AWS", "NCP", "Docker", "Kubernetes", "Jenkins",
               "GitHub Actions", "Datadog", "Prometheus", "Grafana"],
    "Tools": ["Git", "Notion", "Slack"],
}

THEMES = {
    "light": dict(card="#FAFAFA", border="#E5E7EB", title="#4F46E5",
                  pill="#FFFFFF", pill_border="#E5E7EB", text="#374151"),
    "dark":  dict(card="#161B22", border="#30363D", title="#A5B4FC",
                  pill="#0D1117", pill_border="#30363D", text="#C9D1D9"),
}

# 레이아웃 (px)
WIDTH, COLS, GAP = 920, 2, 24
CARD_PAD, CARD_RADIUS = 24, 16
TITLE_SIZE, TITLE_GAP = 16, 18
PILL_FONT, PILL_H, PILL_PAD_X, PILL_RADIUS, PILL_GAP = 15, 34, 14, 8, 10
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"

# Helvetica 글리프 폭 (1000 단위). 시스템 폰트별 오차는 PILL_PAD_X 여유로 흡수.
CHAR_W = {
    **dict(zip("abcdefghijklmnopqrstuvwxyz",
               [556, 556, 500, 556, 556, 278, 556, 556, 222, 222, 500, 222, 833,
                556, 556, 556, 556, 333, 500, 278, 556, 500, 722, 500, 500, 500])),
    **dict(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ",
               [667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667, 556, 833,
                722, 778, 667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611])),
    **{d: 556 for d in "0123456789"},
    " ": 278, "/": 278, "-": 333, ".": 278, "+": 584,
}


def text_width(s: str, size: float) -> float:
    return sum(CHAR_W.get(c, 600) for c in s) / 1000 * size


def layout_card(items: list[str], card_w: int) -> tuple[list[tuple[float, float, float, str]], int]:
    """pill (x, y, w, label) 목록과 카드 높이를 반환. 좌표는 카드 기준."""
    inner_w = card_w - CARD_PAD * 2
    x, y = CARD_PAD, CARD_PAD + TITLE_SIZE + TITLE_GAP
    pills = []
    for label in items:
        w = round(text_width(label, PILL_FONT) + PILL_PAD_X * 2)
        if x + w > CARD_PAD + inner_w and x > CARD_PAD:  # 줄바꿈
            x, y = CARD_PAD, y + PILL_H + PILL_GAP
        pills.append((x, y, w, label))
        x += w + PILL_GAP
    return pills, y + PILL_H + CARD_PAD


def render(theme: dict) -> str:
    card_w = (WIDTH - GAP * (COLS - 1)) // COLS
    cards = [(title, *layout_card(items, card_w)) for title, items in SKILLS.items()]
    rows = [cards[i:i + COLS] for i in range(0, len(cards), COLS)]

    out, y0 = [], 0
    for row in rows:
        row_h = max(h for _, _, h in row)
        for col, (title, pills, _) in enumerate(row):
            x0 = col * (card_w + GAP)
            out.append(
                f'<rect x="{x0 + 0.5}" y="{y0 + 0.5}" width="{card_w - 1}" height="{row_h - 1}" '
                f'rx="{CARD_RADIUS}" fill="{theme["card"]}" stroke="{theme["border"]}"/>')
            out.append(
                f'<text x="{x0 + CARD_PAD}" y="{y0 + CARD_PAD + TITLE_SIZE - 3}" '
                f'font-size="{TITLE_SIZE}" font-weight="600" fill="{theme["title"]}">{escape(title)}</text>')
            for px, py, pw, label in pills:
                out.append(
                    f'<rect x="{x0 + px + 0.5}" y="{y0 + py + 0.5}" width="{pw - 1}" height="{PILL_H - 1}" '
                    f'rx="{PILL_RADIUS}" fill="{theme["pill"]}" stroke="{theme["pill_border"]}"/>')
                out.append(
                    f'<text x="{x0 + px + pw / 2}" y="{y0 + py + PILL_H / 2}" text-anchor="middle" '
                    f'dominant-baseline="central" font-size="{PILL_FONT}" fill="{theme["text"]}">{escape(label)}</text>')
        y0 += row_h + GAP
    height = y0 - GAP

    body = "\n  ".join(out)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
        f'viewBox="0 0 {WIDTH} {height}" font-family="{FONT}">\n  {body}\n</svg>\n'
    )


if __name__ == "__main__":
    assets = Path(__file__).resolve().parent.parent / "assets"
    assets.mkdir(exist_ok=True)
    for name, theme in THEMES.items():
        path = assets / f"skills-{name}.svg"
        path.write_text(render(theme), encoding="utf-8")
        print(f"wrote {path.relative_to(assets.parent)}")
