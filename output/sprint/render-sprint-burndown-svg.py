"""Render the Sprint 1 burndown (ideal vs actual remaining SWP) as a standalone SVG for progress-report.md."""
import json
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE.parents[1] / "reports" / "sprint-1-burndown.svg"
W, H, L, R, T, B = 720, 380, 60, 150, 40, 50  # size + margins (right margin holds the legend)


def main():
    sim = json.loads((HERE / "sprint-1-simulation.json").read_text(encoding="utf-8"))
    pts, top = sim["burndown"], sim["committed_swp"]
    n = len(pts) - 1
    x = lambda i: L + (W - L - R) * i / n
    y = lambda v: T + (H - T - B) * (1 - v / top)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
             'font-family="Segoe UI, Arial, sans-serif" font-size="12">',
             f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
             f'<text x="{L}" y="24" font-size="15" font-weight="600" fill="#1f2328">'
             f'Burndown {sim["iteration"]} ({sim["start"]} → {sim["end"]}) — SWP còn lại</text>']
    for v in range(0, top + 1, 20):
        parts.append(f'<line x1="{L}" y1="{y(v):.1f}" x2="{W - R}" y2="{y(v):.1f}" stroke="#e5e7eb"/>'
                     f'<text x="{L - 8}" y="{y(v) + 4:.1f}" text-anchor="end" fill="#57606a">{v}</text>')
    for p in pts:
        label = "D0" if p["day"] == 0 else f'D{p["day"]}'
        parts.append(f'<text x="{x(p["day"]):.1f}" y="{H - B + 18}" text-anchor="middle" fill="#57606a">{label}</text>')
    parts.append(f'<text x="{(L + W - R) / 2}" y="{H - 12}" text-anchor="middle" fill="#57606a">'
                 'Ngày làm việc (D1 = 2026/11/16, D10 = 2026/11/27)</text>')
    ideal = " ".join(f'{x(p["day"]):.1f},{y(p["ideal"]):.1f}' for p in pts)
    actual = " ".join(f'{x(p["day"]):.1f},{y(p["remaining"]):.1f}' for p in pts)
    parts.append(f'<polyline points="{ideal}" fill="none" stroke="#8c959f" stroke-width="2" stroke-dasharray="6 4"/>')
    parts.append(f'<polyline points="{actual}" fill="none" stroke="#cf222e" stroke-width="2.5"/>')
    for p in pts:
        parts.append(f'<circle cx="{x(p["day"]):.1f}" cy="{y(p["remaining"]):.1f}" r="3" fill="#cf222e"/>')
    last = pts[-1]
    parts.append(f'<text x="{x(n) + 6:.1f}" y="{y(last["remaining"]) - 6:.1f}" fill="#cf222e" font-weight="600">'
                 f'{last["remaining"]}</text>')
    lx = W - R + 20
    parts += [f'<line x1="{lx}" y1="60" x2="{lx + 24}" y2="60" stroke="#8c959f" stroke-width="2" stroke-dasharray="6 4"/>',
              f'<text x="{lx + 30}" y="64" fill="#1f2328">Kế hoạch</text>',
              f'<line x1="{lx}" y1="84" x2="{lx + 24}" y2="84" stroke="#cf222e" stroke-width="2.5"/>',
              f'<text x="{lx + 30}" y="88" fill="#1f2328">Thực tế (Done)</text>',
              f'<text x="{lx}" y="116" fill="#57606a">Cam kết: {top} SWP</text>',
              f'<text x="{lx}" y="134" fill="#57606a">Còn lại: {last["remaining"]} SWP</text>', "</svg>"]
    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
