from __future__ import annotations

import html


TOP_CATEGORIES = ["Materiales", "Maquinaria", "Metodos"]
BOTTOM_CATEGORIES = ["Mano de Obra", "Medio Ambiente", "Medicion"]


def _wrap(text: str, max_chars: int = 22) -> list[str]:
    words = str(text).split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) > max_chars and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines[:2] or [""]


def _text(x: int, y: int, text: str, *, color: str = "#102033", size: int = 12, weight: int = 500, anchor: str = "middle") -> str:
    lines = _wrap(text)
    start_y = y - (len(lines) - 1) * 7
    spans = []
    for idx, line in enumerate(lines):
        spans.append(f"<tspan x='{x}' y='{start_y + idx * 15}'>{html.escape(line)}</tspan>")
    return f"<text text-anchor='{anchor}' font-family='Inter, Arial, sans-serif' font-size='{size}' font-weight='{weight}' fill='{color}'>{''.join(spans)}</text>"


def _box(x: int, y: int, w: int, h: int, text: str, *, fill: str, stroke: str, color: str, weight: int = 700) -> str:
    return (
        f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='12' fill='{fill}' stroke='{stroke}' stroke-width='1.3'/>"
        + _text(x + w // 2, y + h // 2 + 5, text, color=color, size=12, weight=weight)
    )


def _cause_box(x: int, y: int, text: str) -> str:
    return _box(x, y, 180, 38, text, fill="#ffffff", stroke="#9bd8cf", color="#102033", weight=500)


def _cat_box(x: int, y: int, text: str) -> str:
    return _box(x, y, 130, 46, text, fill="#00a88f", stroke="#00a88f", color="#ffffff", weight=800)


def _line(x1: int, y1: int, x2: int, y2: int, *, color: str, width: float = 2.0, arrow: bool = False) -> str:
    marker = " marker-end='url(#arrow-teal)'" if arrow else ""
    return f"<line x1='{x1}' y1='{y1}' x2='{x2}' y2='{y2}' stroke='{color}' stroke-width='{width}' stroke-linecap='round'{marker}/>"


def _poly(points: list[tuple[int, int]], *, color: str, width: float = 2.0, arrow: bool = False) -> str:
    marker = " marker-end='url(#arrow-teal)'" if arrow else ""
    pts = " ".join(f"{x},{y}" for x, y in points)
    return f"<polyline points='{pts}' fill='none' stroke='{color}' stroke-width='{width}' stroke-linecap='round' stroke-linejoin='round'{marker}/>"


def _category_group(category: str, center_x: int, top: bool, causes: dict[str, list[str]]) -> str:
    teal = "#008f7a"
    spine_y = 430
    cat_w = 130
    cat_h = 46
    cat_x = center_x - cat_w // 2
    cat_y = 225 if top else 590
    cat_cx = center_x
    cat_cy = cat_y + cat_h // 2
    cause_x = center_x - 248
    bus_x = center_x - 82
    # Causes are stacked from the central spine outward.
    cause_ys = [360, 315, 270, 225, 180, 135, 90] if top else [450, 495, 540, 585, 630, 675, 720]
    max_causes = min(len(causes.get(category, [])[:7]) or 1, 7)
    used_y = [y + 19 for y in cause_ys[:max_causes]] + [cat_cy]
    bus_top = min(used_y)
    bus_bottom = max(used_y)

    parts: list[str] = []
    # Main fishbone branch.
    parts.append(_line(center_x, spine_y, cat_cx, cat_cy, color=teal, width=4.0))
    parts.append(_cat_box(cat_x, cat_y, category))

    cat_causes = causes.get(category, [])[:7]
    parts.append(_line(bus_x, bus_top, bus_x, bus_bottom, color=teal, width=2.4))
    parts.append(_poly([(bus_x, cat_cy), (cat_x, cat_cy)], color=teal, width=2.4, arrow=True))

    for idx, cause in enumerate(cat_causes):
        y = cause_ys[idx]
        parts.append(_cause_box(cause_x, y, cause))
        parts.append(_poly([(cause_x + 180, y + 19), (bus_x, y + 19)], color=teal, width=2.2, arrow=True))
    return "".join(parts)


def ishikawa_svg(effect: str, causes: dict[str, list[str]]) -> str:
    navy = "#08264a"
    width, height = 1450, 980
    centers = [430, 740, 1050]
    parts = [
        f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {width} {height}' width='100%' height='100%' role='img'>",
        "<defs>",
        "<marker id='arrow-teal' markerWidth='8' markerHeight='8' refX='7' refY='4' orient='auto'><path d='M0,0 L8,4 L0,8 Z' fill='#00a88f'/></marker>",
        "<marker id='arrow-navy' markerWidth='12' markerHeight='12' refX='11' refY='6' orient='auto'><path d='M0,0 L12,6 L0,12 Z' fill='#08264a'/></marker>",
        "</defs>",
        "<rect width='100%' height='100%' fill='#ffffff'/>",
        # Main spine and tail.
        f"<path d='M 60 430 L 1200 430' fill='none' stroke='{navy}' stroke-width='6' stroke-linecap='round' marker-end='url(#arrow-navy)'/>",
        f"<path d='M 18 430 L 82 495 L 82 365 Z' fill='{navy}'/>",
        _box(1225, 390, 170, 80, effect, fill=navy, stroke=navy, color="#ffffff", weight=800),
    ]

    for cat, cx in zip(TOP_CATEGORIES, centers):
        parts.append(_category_group(cat, cx, True, causes))
    for cat, cx in zip(BOTTOM_CATEGORIES, centers):
        parts.append(_category_group(cat, cx, False, causes))

    parts.append("</svg>")
    return "".join(parts)


def ishikawa_html(effect: str, causes: dict[str, list[str]]) -> str:
    svg = ishikawa_svg(effect, causes)
    return f"""
    <div style="width:100%;height:760px;background:#f8fbf8;border-radius:16px;border:1px solid #dbe8dd;position:relative;overflow:hidden;font-family:Inter,Arial,sans-serif;">
      <div style="position:absolute;right:14px;top:12px;z-index:10;display:flex;gap:8px;align-items:center;background:white;border:1px solid #dbe8dd;border-radius:12px;padding:6px 8px;box-shadow:0 8px 22px rgba(0,0,0,.08);">
        <button onclick="zoomIsh(0.1)" style="border:0;background:#edf8ef;border-radius:8px;padding:7px 10px;cursor:pointer;font-weight:800;">+</button>
        <button onclick="zoomIsh(-0.1)" style="border:0;background:#edf8ef;border-radius:8px;padding:7px 11px;cursor:pointer;font-weight:800;">-</button>
        <button onclick="resetIsh()" style="border:0;background:#edf8ef;border-radius:8px;padding:7px 10px;cursor:pointer;font-weight:700;">Reset</button>
        <span id="zoomLabel" style="font-size:12px;color:#335;min-width:42px;text-align:right;">75%</span>
      </div>
      <div id="ishViewport" style="width:100%;height:100%;overflow:auto;cursor:grab;background:white;">
        <div id="ishCanvas" style="width:1450px;height:980px;transform:scale(.72);transform-origin:top left;transition:transform .12s ease;">
          {svg}
        </div>
      </div>
    </div>
    <script>
      let ishZoom = 0.72;
      const canvas = document.getElementById('ishCanvas');
      const viewport = document.getElementById('ishViewport');
      const label = document.getElementById('zoomLabel');
      function applyZoom() {{
        canvas.style.transform = `scale(${{ishZoom}})`;
        canvas.style.width = `${{1450 * ishZoom}}px`;
        canvas.style.height = `${{980 * ishZoom}}px`;
        label.innerText = `${{Math.round(ishZoom * 100)}}%`;
      }}
      function zoomIsh(delta) {{ ishZoom = Math.max(0.45, Math.min(1.6, ishZoom + delta)); applyZoom(); }}
      function resetIsh() {{ ishZoom = 0.72; applyZoom(); viewport.scrollLeft = 0; viewport.scrollTop = 0; }}
      let dragging = false, startX = 0, startY = 0, scrollLeft = 0, scrollTop = 0;
      viewport.addEventListener('mousedown', e => {{ dragging = true; viewport.style.cursor = 'grabbing'; startX = e.pageX; startY = e.pageY; scrollLeft = viewport.scrollLeft; scrollTop = viewport.scrollTop; }});
      viewport.addEventListener('mouseup', () => {{ dragging = false; viewport.style.cursor = 'grab'; }});
      viewport.addEventListener('mouseleave', () => {{ dragging = false; viewport.style.cursor = 'grab'; }});
      viewport.addEventListener('mousemove', e => {{ if (!dragging) return; e.preventDefault(); viewport.scrollLeft = scrollLeft - (e.pageX - startX); viewport.scrollTop = scrollTop - (e.pageY - startY); }});
      applyZoom();
    </script>
    """
