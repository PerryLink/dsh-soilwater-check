#!/usr/bin/env python3
"""README visuals for dsh-soilwater-check — derived from this plugin's real pipeline.

Two figures, both read off the shipped material rather than a shared template:

  hero 1440×576 (Pillow, 4 files: zh/en × light/dark)
      The signature check, SW-005. Row 1 of the register carries three cells
      that must agree: 监测结果 80, 标准限值 60, 超标情况 达标. The relation
      diagram compares the two numbers the register itself states (80 > 60),
      shows the verdict that should follow (应判「超标」) against the verdict
      actually written (达标), and marks the disagreement at its locator
      (第 1 行 · field exceed). The strip below reports 1 issue, 0 skipped and
      leaves the verdict to the reviewer.

  flow 1100×660 (hand-written SVG, 2 files: light/dark)
      One register, inspected at three scopes — a three-view structure rather
      than a row of boxes:
        ① 表头        project / phase / checkedAt          → SW-007
        ② 单行 × 栏   点位·项目 / 结果 / 日期 / 标准        → SW-001/002/003/004/008
        ③ 跨行·跨栏   样品编号栏全表唯一；结果×限值×判定    → SW-006 / SW-005
      The three views converge on one report: issues[] (row + field locator)
      and skipped[] (reason), with the verdict left to the reviewer. The right
      column is the control surface that shapes every check: evidence kind →
      severity cap, the 8/8 citation gap, and the config keys.

Every value in the figures comes from the repository's own fixtures:
  tests/fixtures/SW-005/SW-005-unsafe.json  (S1 表层土 · 砷 · 80 vs 60 · 达标)
  tests/fixtures/SW-006/SW-006-unsafe.json  (TR-2026-0018 repeated)
  rules/soilwater-check.yaml                (SW-001..SW-008, kinds, severity)
  src/model.ts                              (header keys, column aliases)

Run once:  python scripts/gen-readme-assets.py
Requires:  Pillow + Windows fonts msyh.ttc / msyhbd.ttc / consola.ttf.
"""
from __future__ import annotations

import os
from html import escape

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")

FONT_CJK = r"C:\Windows\Fonts\msyh.ttc"
FONT_CJK_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
FONT_MONO = r"C:\Windows\Fonts\consola.ttf"
FONT_MONO_BOLD = r"C:\Windows\Fonts\consolab.ttf"
for _p in (FONT_CJK, FONT_CJK_BOLD, FONT_MONO, FONT_MONO_BOLD):
    if not os.path.exists(_p):
        raise SystemExit(f"FATAL: font missing: {_p}")

FONT_FILES = {
    "cjk": FONT_CJK,
    "cjk_bold": FONT_CJK_BOLD,
    "mono": FONT_MONO,
    "mono_bold": FONT_MONO_BOLD,
}

SKIN = {
    "light": dict(
        bg_from="#f9f6fd", bg_to="#e4eaf8",
        card="#ffffff", edge="#e6e2ef",
        text="#141419", sub="#4d5261", faint="#8f94a4",
        accent="#4B67B4", accent2="#16a34a",
        pill="#ece7f9", band="#f5f2fb", grid="#e7e4f0",
        amber="#b45309", amber_bg="#fdf3e9",
        shadow=(32, 26, 64), shadow_alpha=64,
    ),
    "dark": dict(
        bg_from="#131a2a", bg_to="#0c1016",
        card="#1b2231", edge="#2e374b",
        text="#f0f3f9", sub="#a8b1c4", faint="#737b8d",
        accent="#8496f5", accent2="#3fb950",
        pill="#242d42", band="#202839", grid="#262f42",
        amber="#d9a441", amber_bg="#2a2216",
        shadow=(0, 0, 0), shadow_alpha=96,
    ),
}


def font(size: float, kind: str = "cjk_bold") -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_FILES[kind], int(round(size)))


def hx(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def gradient(w: int, h: int, c1: str, c2: str) -> Image.Image:
    base = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(base)
    a, b = hx(c1), hx(c2)
    for y in range(h):
        t = 0.12 * (y / h) + 0.88 * (y / h) ** 1.35
        draw.line([(0, y), (w, y)],
                  fill=tuple(int(p + (q - p) * t) for p, q in zip(a, b)))
    return base


def glow(img: Image.Image, cx: int, cy: int, radius: int,
         color: tuple[int, int, int], alpha: int = 26) -> Image.Image:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for step in range(10, 0, -1):
        r = radius * step / 10
        draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                     fill=color + (int(alpha * (1 - step / 11)),))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def card(img: Image.Image, box: tuple[int, int, int, int], skin: str,
         radius: int = 22, shadow: int = 26) -> Image.Image:
    """A soft-shadowed rounded card over the gradient background."""
    s = SKIN[skin]
    x0, y0, x1, y1 = box
    shade = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(shade)
    d.rounded_rectangle([x0 + 2, y0 + 10, x1 - 2, y1 + 14],
                        radius=radius, fill=s["shadow"] + (s["shadow_alpha"],))
    shade = shade.filter(ImageFilter.GaussianBlur(12))
    base = Image.alpha_composite(img.convert("RGBA"), shade)
    d = ImageDraw.Draw(base)
    d.rounded_rectangle(box, radius=radius, fill=hx(s["card"]),
                        outline=hx(s["edge"]), width=2)
    return base.convert("RGB")


_SCRATCH = ImageDraw.Draw(Image.new("RGB", (8, 8)))


def measure(text: str, size: float, kind: str) -> float:
    return _SCRATCH.textlength(text, font=font(size, kind))


def require_w(text: str, size: float, kind: str, max_w: float,
              what: str) -> float:
    width = measure(text, size, kind)
    if width > max_w + 0.4:
        raise SystemExit(
            f"FATAL: {what} overflows: {text!r} needs {width:.1f}px > {max_w}px")
    return width


def fit(text: str, kind: str, max_w: float, start: int, minimum: int) -> int:
    size = start
    while size > minimum:
        if measure(text, size, kind) <= max_w:
            return size
        size -= 1
    if measure(text, minimum, kind) <= max_w:
        return minimum
    raise SystemExit(
        f"FATAL: text does not fit {max_w}px at >= {minimum}px: {text!r}")


def pill(img: Image.Image, xy: tuple[int, int], text: str, skin: str,
         size: float = 15, fg: str | None = None,
         bg: str | None = None) -> tuple[int, int]:
    s = SKIN[skin]
    d = ImageDraw.Draw(img)
    f = font(size, "cjk_bold")
    w = d.textlength(text, font=f)
    x, y = xy
    h = size + 22
    d.rounded_rectangle([x, y, x + w + 32, y + h], radius=h // 2,
                        fill=hx(bg or s["pill"]))
    d.text((x + 16, y + h / 2), text, font=f, fill=hx(fg or s["accent"]),
           anchor="lm")
    return int(x + w + 32), int(y + h)


def chip(img: Image.Image, xy: tuple[int, int], text: str, fg: str, bg: str,
         size: float = 11, kind: str = "cjk_bold", padx: int = 10,
         height: int = 22) -> int:
    d = ImageDraw.Draw(img)
    f = font(size, kind)
    w = d.textlength(text, font=f)
    x, y = xy
    d.rounded_rectangle([x, y, x + w + padx * 2, y + height],
                        radius=height // 2, fill=hx(bg))
    d.text((x + padx, y + height / 2), text, font=f, fill=hx(fg), anchor="lm")
    return int(w + padx * 2)


def arrow_right(d: ImageDraw.ImageDraw, x0: float, x1: float, y: float,
                color: str, width: int = 2, head: int = 9) -> None:
    d.line([(x0, y), (x1 - head + 1, y)], fill=hx(color), width=width)
    d.polygon([(x1, y), (x1 - head, y - head * 0.55),
               (x1 - head, y + head * 0.55)], fill=hx(color))


def cross_badge(d: ImageDraw.ImageDraw, cx: float, cy: float, r: float,
                color: str, bg: str) -> None:
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=hx(bg),
              outline=hx(color), width=2)
    k = r * 0.45
    d.line([(cx - k, cy - k), (cx + k, cy + k)], fill=hx(color), width=3)
    d.line([(cx + k, cy - k), (cx - k, cy + k)], fill=hx(color), width=3)


# --------------------------------------------------------------------------- hero
# The copy is checked against the plugin's fixture, not invented. `result`,
# `limit` and `verdict` are the three cells SW-005 reads together.
HERO = {
    "zh": dict(
        kicker="DeepSeek Harness 插件 · 核查器",
        value=["只核对台账自身的齐备与算术", "差在哪一行、哪一栏，逐条指认"],
        sub=["八条版本化规则分别读表头、读每一行、读跨行与跨栏的关系；",
             "未执行的检查进 skipped 并写明原因，结论留给审核人。"],
        meta=["soilwater_check · SW-001..SW-008 · rules v2026.1",
              "rules/soilwater-check.yaml · issues[] + skipped[] · all <= warn"],
        foot="Apache-2.0 · PerryLink DSH plugin family · 只读材料 · 不联网",
        row_title="监测台账 · 第 1 行",
        row_chip="只读原件",
        row_sub="S1 表层土 · 砷 · TR-2026-0018 · 2026-03-05 · GB 36600",
        row_note="示例值取自 tests/fixtures/SW-005/SW-005-unsafe.json",
        tiles=[("监测结果", "80"), ("标准限值", "60"), ("超标情况", "达标")],
        rule_title="SW-005 · 三栏联动",
        rule_sub="只比台账自己写的两个数，再核对判定",
        box_a=("监测结果", "80"),
        box_b=("标准限值", "60"),
        expected=["80 > 60", "应判「超标」"],
        actual=["超标情况", "达标"],
        band="关系与判定不符：80 > 60，却写「达标」",
        locator="locator · 第 1 行 · field exceed",
        fix="建议核对三个数值与判定；本条不判断限值是否取对了标准",
        strip_l="issues[] 1 条差异 · skipped[] 0 条未执行",
        strip_r="结论留给审核人",
    ),
    "en": dict(
        kicker="DeepSeek Harness plugin · checker",
        value=["Completeness and arithmetic,", "row and column, named exactly"],
        sub=["Eight rules read the header, each row, and the cross-column relations;",
             "unrun checks go to skipped with a reason; the verdict stays human."],
        meta=["soilwater_check · SW-001..SW-008 · rule pack v2026.1",
              "rules/soilwater-check.yaml · issues[] + skipped[] · all capped at warn"],
        foot="Apache-2.0 · PerryLink DSH plugin family · read-only on the material",
        row_title="Monitoring register · row 1",
        row_chip="read-only",
        row_sub="S1 topsoil · arsenic · TR-2026-0018 · 2026-03-05 · GB 36600",
        row_note="values from tests/fixtures/SW-005/SW-005-unsafe.json",
        tiles=[("RESULT", "80"), ("LIMIT", "60"), ("VERDICT", "pass")],
        rule_title="SW-005 · three-column check",
        rule_sub="Compares the two numbers the register itself states",
        box_a=("RESULT", "80"),
        box_b=("LIMIT", "60"),
        expected=["80 > 60", "over limit"],
        actual=["VERDICT", "pass"],
        band="80 > 60, yet the register says pass",
        locator="locator · row 1 · field exceed",
        fix="check the three values and the verdict; it never checks which standard the limit came from",
        strip_l="issues[] 1 finding · skipped[] 0 not run",
        strip_r="verdict stays human",
    ),
}


def hero(lang: str, skin: str) -> None:
    H = HERO[lang]
    s = SKIN[skin]
    W, HT = 1440, 576
    img = gradient(W, HT, s["bg_from"], s["bg_to"])
    img = glow(img, 1120, 110, 520, hx(s["accent"]), 22 if skin == "light" else 26)
    d = ImageDraw.Draw(img)

    # ---- left column --------------------------------------------------------
    pill(img, (72, 54), H["kicker"], skin, size=15)
    title = "dsh-soilwater-check"
    title_size = fit(title, "cjk_bold", 618, 56, 48)
    d = ImageDraw.Draw(img)
    d.text((72, 116), title, font=font(title_size, "cjk_bold"),
           fill=hx(s["text"]))
    require_w(title, title_size, "cjk_bold", 618, "hero title")

    value_size = 34
    d.text((72, 234), H["value"][0], font=font(value_size, "cjk_bold"),
           fill=hx(s["text"]))
    d.text((72, 292), H["value"][1], font=font(value_size, "cjk_bold"),
           fill=hx(s["text"]))
    for line in H["value"]:
        require_w(line, value_size, "cjk_bold", 618, "hero value line")

    for index, line in enumerate(H["sub"]):
        d.text((72, 364 + index * 30), line, font=font(17, "cjk"),
               fill=hx(s["sub"]))
        require_w(line, 17, "cjk", 618, "hero sub line")
    for index, line in enumerate(H["meta"]):
        d.text((72, 456 + index * 24), line, font=font(14, "mono"),
               fill=hx(s["faint"]))
        require_w(line, 14, "mono", 618, "hero meta line")
    d.text((72, 522), H["foot"], font=font(12.5, "cjk"), fill=hx(s["faint"]))
    require_w(H["foot"], 12.5, "cjk", 618, "hero foot")

    # ---- card A: the row under inspection ----------------------------------
    img = card(img, (716, 44, 1376, 208), skin, radius=22, shadow=26)
    d = ImageDraw.Draw(img)
    d.text((740, 58), H["row_title"], font=font(16, "cjk_bold"),
           fill=hx(s["text"]))
    require_w(H["row_title"], 16, "cjk_bold", 430, "hero row title")
    chip_w = int(measure(H["row_chip"], 11, "cjk_bold") + 20)
    d.rounded_rectangle([1352 - chip_w, 56, 1352, 78], radius=11,
                        fill=hx(s["pill"]))
    d.text((1352 - chip_w + 10, 67), H["row_chip"], font=font(11, "cjk_bold"),
           fill=hx(s["accent"]), anchor="lm")

    d.text((740, 84), H["row_sub"], font=font(12.5, "cjk"), fill=hx(s["sub"]))
    require_w(H["row_sub"], 12.5, "cjk", 612, "hero row sub")

    tile_boxes = [(740, 108, 940, 168), (956, 108, 1156, 168),
                  (1172, 108, 1352, 168)]
    for index, (label, value) in enumerate(H["tiles"]):
        box = tile_boxes[index]
        d.rounded_rectangle(box, radius=14, fill=hx(s["band"]),
                            outline=hx(s["edge"]), width=1)
        d.text((box[0] + 16, box[1] + 10), label, font=font(10.5, "cjk"),
               fill=hx(s["faint"]))
        value_font = font(25, "mono_bold") if value.isdigit() else font(24, "cjk_bold")
        d.text((box[0] + 16, box[1] + 28), value, font=value_font,
               fill=hx(s["amber"] if index == 2 else s["text"]))
        require_w(label, 10.5, "cjk", (box[2] - box[0]) - 32, "hero tile label")
        require_w(value, 25, "mono_bold" if value.isdigit() else "cjk_bold",
                  (box[2] - box[0]) - 32, "hero tile value")
    d.text((740, 180), H["row_note"], font=font(11, "cjk"),
           fill=hx(s["faint"]))
    require_w(H["row_note"], 11, "cjk", 612, "hero row note")

    # ---- card B: the SW-005 relation ---------------------------------------
    img = card(img, (716, 220, 1376, 452), skin, radius=22, shadow=24)
    d = ImageDraw.Draw(img)
    d.text((740, 238), H["rule_title"], font=font(15, "cjk_bold"),
           fill=hx(s["accent"]))
    require_w(H["rule_title"], 15, "cjk_bold", 430, "hero rule title")
    warn_w = int(measure("warn", 10.5, "mono_bold") + 20)
    warn_x = 740 + measure(H["rule_title"], 15, "cjk_bold") + 12
    d.rounded_rectangle([warn_x, 236, warn_x + warn_w, 256], radius=10,
                        fill=hx(s["amber_bg"]))
    d.text((warn_x + 10, 246), "warn", font=font(10.5, "mono_bold"),
           fill=hx(s["amber"]), anchor="lm")
    d.text((740, 262), H["rule_sub"], font=font(11.5, "cjk"),
           fill=hx(s["sub"]))
    require_w(H["rule_sub"], 11.5, "cjk", 612, "hero rule sub")

    # three register cells plus the two cells the relation reads
    box_y0, box_y1 = 288, 344

    def relation_box(box: tuple[int, int, int, int],
                     label: str, value: str,
                     accent: str | None = None) -> None:
        d.rounded_rectangle(box, radius=13, fill=hx(s["band"]),
                            outline=hx(accent or s["edge"]), width=2 if accent else 1)
        d.text((box[0] + 14, box[1] + 9), label, font=font(10.5, "cjk"),
               fill=hx(s["faint"]))
        value_font = font(23, "mono_bold") if value.isdigit() else font(22, "cjk_bold")
        d.text((box[0] + 14, box[1] + 26), value, font=value_font,
               fill=hx(accent or s["text"]))
        require_w(label, 10.5, "cjk", (box[2] - box[0]) - 28, "relation label")
        require_w(value, 23, "mono_bold" if value.isdigit() else "cjk_bold",
                  (box[2] - box[0]) - 28, "relation value")

    relation_box((744, box_y0, 852, box_y1), H["box_a"][0], H["box_a"][1])
    d = ImageDraw.Draw(img)
    d.text((864, 302), ">", font=font(24, "cjk_bold"), fill=hx(s["accent"]),
           anchor="mm")
    relation_box((880, box_y0, 988, box_y1), H["box_b"][0], H["box_b"][1])
    arrow_right(d, 998, 1026, 316, s["accent"], width=2, head=8)
    # expected outcome
    d.rounded_rectangle([1032, 288, 1164, 344], radius=13, fill=hx(s["amber_bg"]),
                        outline=hx(s["amber"]), width=2)
    d.text((1046, 296), H["expected"][0], font=font(11, "mono_bold"),
           fill=hx(s["amber"]))
    d.text((1046, 316), H["expected"][1], font=font(12.5, "cjk_bold"),
           fill=hx(s["amber"]))
    require_w(H["expected"][1], 12.5, "cjk_bold", 104, "hero expected")
    # actual verdict
    d.rounded_rectangle([1180, 288, 1352, 344], radius=13, fill=hx(s["band"]),
                        outline=hx(s["amber"]), width=2)
    d.text((1194, 296), H["actual"][0], font=font(10.5, "cjk"),
           fill=hx(s["faint"]))
    d.text((1194, 314), H["actual"][1], font=font(22, "cjk_bold"),
           fill=hx(s["amber"]))
    require_w(H["actual"][1], 22, "cjk_bold", 120, "hero actual")
    cross_badge(d, 1322, 304, 12, s["amber"], s["card"])

    # disagreement band
    d.rounded_rectangle([1032, 356, 1352, 388], radius=12,
                        fill=hx(s["amber_bg"]))
    d.text((1044, 365), H["band"], font=font(11.5, "cjk"), fill=hx(s["amber"]))
    require_w(H["band"], 11.5, "cjk", 296, "hero disagreement band")

    d.text((744, 404), H["locator"], font=font(11, "cjk"),
           fill=hx(s["faint"]))
    require_w(H["locator"], 11, "cjk", 612, "hero locator")
    d.text((744, 428), H["fix"], font=font(11, "cjk"), fill=hx(s["faint"]))
    require_w(H["fix"], 11, "cjk", 612, "hero fix")

    # ---- strip: the report line --------------------------------------------
    img = card(img, (716, 464, 1376, 516), skin, radius=18, shadow=16)
    d = ImageDraw.Draw(img)
    d.text((740, 480), H["strip_l"], font=font(13, "cjk"), fill=hx(s["text"]))
    right_w = measure(H["strip_r"], 13, "cjk_bold")
    d.text((1352 - right_w, 480), H["strip_r"], font=font(13, "cjk_bold"),
           fill=hx(s["accent2"]))
    require_w(H["strip_l"], 13, "cjk", 500, "hero strip left")
    require_w(H["strip_r"], 13, "cjk_bold", 160, "hero strip right")

    name = f"dsh-soilwater-check-hero-{lang}-{skin}.webp"
    img.save(os.path.join(OUT, name), "WEBP", quality=92, method=6)
    print(f"wrote {name} ({W}×{HT})")


# --------------------------------------------------------------------------- flow
FLOW = {
    "light": dict(
        bg_from="#f9f6fd", bg_to="#e4eaf8",
        panel="#ffffff", card="#ffffff", edge="#e6e2ef", band="#f5f2fb",
        band2="#fbf9fe", text="#141419", sub="#4d5261", faint="#8f94a4",
        accent="#4B67B4", accent2="#16a34a", amber="#b45309",
        amber_bg="#fdf3e9", rule="#dcd8ea", shadow="0.10", shadow_color="#16122c",
    ),
    "dark": dict(
        bg_from="#131a2a", bg_to="#0c1016",
        panel="#1b2231", card="#1b2231", edge="#2e374b", band="#202839",
        band2="#1e2534", text="#f0f3f9", sub="#a8b1c4", faint="#737b8d",
        accent="#8496f5", accent2="#3fb950", amber="#d9a441",
        amber_bg="#2a2216", rule="#2b3348", shadow="0.45", shadow_color="#000000",
    ),
}

FONT_CSS_CJK = ("'Microsoft YaHei','PingFang SC','Noto Sans CJK SC',"
                "'Source Han Sans SC',sans-serif")
FONT_CSS_MONO = "'Consolas','SFMono-Regular','Menlo',ui-monospace,monospace"


class Svg:
    """Tiny SVG writer that measures every label before emitting it."""

    def __init__(self) -> None:
        self.parts: list[str] = []
        self.overflows: list[str] = []

    def add(self, markup: str) -> None:
        self.parts.append(markup)

    def text(self, x: float, y: float, content: str, size: float, fill: str, *,
             anchor: str = "start", weight: int | None = None,
             mono: bool = False, max_w: float | None = None,
             opacity: float | None = None) -> None:
        kind = "mono_bold" if (mono and weight) else (
            "mono" if mono else ("cjk_bold" if weight else "cjk"))
        if max_w is not None:
            width = measure(content, size, kind)
            if width > max_w + 0.4:
                self.overflows.append(
                    f"{content!r} needs {width:.1f}px > {max_w}px")
        family = FONT_CSS_MONO if mono else FONT_CSS_CJK
        attrs = [f'x="{x}"', f'y="{y}"', f'fill="{fill}"',
                 f'font-family="{family}"', f'font-size="{size}"']
        if anchor != "start":
            attrs.append(f'text-anchor="{anchor}"')
        if weight:
            attrs.append(f'font-weight="{weight}"')
        if opacity is not None:
            attrs.append(f'opacity="{opacity}"')
        self.add(f'<text {" ".join(attrs)}>{escape(content)}</text>')

    def rect(self, x: float, y: float, w: float, h: float, *, fill: str,
             rx: float = 0, stroke: str | None = None, sw: float = 1.5,
             shadow: bool = False, opacity: float | None = None) -> None:
        attrs = [f'x="{x}"', f'y="{y}"', f'width="{w}"', f'height="{h}"']
        if rx:
            attrs.append(f'rx="{rx}"')
        attrs.append(f'fill="{fill}"')
        if stroke:
            attrs.append(f'stroke="{stroke}"')
            attrs.append(f'stroke-width="{sw}"')
        if opacity is not None:
            attrs.append(f'opacity="{opacity}"')
        if shadow:
            attrs.append('filter="url(#soft)"')
        self.add(f'<rect {" ".join(attrs)}/>')

    def line(self, x1: float, y1: float, x2: float, y2: float, *, stroke: str,
             sw: float = 1.5, dash: str | None = None,
             marker: str | None = None, opacity: float | None = None) -> None:
        attrs = [f'x1="{x1}"', f'y1="{y1}"', f'x2="{x2}"', f'y2="{y2}"',
                 f'stroke="{stroke}"', f'stroke-width="{sw}"']
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        if marker:
            attrs.append(f'marker-end="url(#{marker})"')
        if opacity is not None:
            attrs.append(f'opacity="{opacity}"')
        self.add(f'<line {" ".join(attrs)}/>')

    def path(self, d: str, *, stroke: str, sw: float = 1.5,
             marker: str | None = None, dash: str | None = None,
             opacity: float | None = None) -> None:
        attrs = [f'd="{d}"', 'fill="none"', f'stroke="{stroke}"',
                 f'stroke-width="{sw}"', 'stroke-linecap="round"']
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        if marker:
            attrs.append(f'marker-end="url(#{marker})"')
        if opacity is not None:
            attrs.append(f'opacity="{opacity}"')
        self.add(f'<path {" ".join(attrs)}/>')

    def circle(self, cx: float, cy: float, r: float, *, fill: str,
               stroke: str | None = None, sw: float = 1.5) -> None:
        attrs = [f'cx="{cx}"', f'cy="{cy}"', f'r="{r}"', f'fill="{fill}"']
        if stroke:
            attrs.append(f'stroke="{stroke}"')
            attrs.append(f'stroke-width="{sw}"')
        self.add(f'<circle {" ".join(attrs)}/>')

    def tag(self, x: float, y: float, rid: str, gloss: str, *, fg: str,
            bg: str, h: float = 26) -> float:
        """A rule chip: mono rule id plus a Chinese gloss; returns its width."""
        id_w = measure(rid, 13, "mono_bold")
        gloss_w = measure(gloss, 11, "cjk") if gloss else 0
        width = 12 + id_w + (8 + gloss_w if gloss else 0) + 12
        self.rect(x, y, width, h, fill=bg, rx=h / 2)
        self.text(x + 12, y + h / 2 + 4.6, rid, 13, fg, mono=True, weight=700,
                  max_w=id_w + 0.4)
        if gloss:
            self.text(x + 12 + id_w + 8, y + h / 2 + 4.2, gloss, 11, fg,
                      max_w=gloss_w + 0.4)
        return width

    def kv_chip(self, x: float, y: float, key: str, gloss: str, *, fg: str,
                bg: str, h: float = 24) -> float:
        key_w = measure(key, 13, "mono_bold")
        gloss_w = measure(gloss, 11, "cjk")
        width = 10 + key_w + 6 + gloss_w + 10
        self.rect(x, y, width, h, fill=bg, rx=8)
        self.text(x + 10, y + h / 2 + 4.4, key, 13, fg, mono=True, weight=700,
                  max_w=key_w + 0.4)
        self.text(x + 10 + key_w + 6, y + h / 2 + 4, gloss, 11, fg,
                  max_w=gloss_w + 0.4)
        return width

    def badge(self, x: float, y: float, label: str, *, fg: str, bg: str,
              h: float = 20, size: float = 11) -> float:
        width = measure(label, size, "mono_bold") + 20
        self.rect(x, y, width, h, fill=bg, rx=h / 2)
        self.text(x + 10, y + h / 2 + size * 0.38, label, size, fg,
                  mono=True, weight=700, max_w=width - 20)
        return width

    def cell(self, x: float, y: float, w: float, h: float, label: str,
             value: str, *, s: dict, mono_value: bool = False,
             accent: str | None = None) -> None:
        self.rect(x, y, w, h, fill=s["band"], rx=9,
                  stroke=accent or s["edge"], sw=1.6 if accent else 1)
        value_kind = "mono_bold" if mono_value else "cjk"
        value_size = 13 if mono_value else 13.5
        if h < 40:
            # compact single-line cell: label on the left, value on the right
            if label:
                self.text(x + 9, y + h / 2 + 4.2, label, 11, s["faint"],
                          max_w=w * 0.45)
                self.text(x + w - 9, y + h / 2 + 4.6, value, value_size,
                          s["text"] if accent is None else accent,
                          mono=mono_value, anchor="end", max_w=w * 0.55,
                          weight=700 if mono_value else None)
            else:
                self.text(x + 9, y + h / 2 + 4.6, value, value_size,
                          s["text"] if accent is None else accent,
                          mono=mono_value, max_w=w - 18,
                          weight=700 if mono_value else None)
            return
        self.text(x + 9, y + 15, label, 11, s["faint"], max_w=w - 18)
        self.text(x + 9, y + h - 9, value, value_size,
                  s["text"] if accent is None else accent,
                  mono=mono_value, max_w=w - 18,
                  weight=700 if mono_value else None)

    def svg(self, w: int, h: int, label: str) -> str:
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" '
                f'height="{h}" viewBox="0 0 {w} {h}" role="img" '
                f'aria-label="{escape(label)}">')
        return "\n".join([head, *self.parts, "</svg>"]) + "\n"


def flow_svg(skin: str) -> str:
    s = FLOW[skin]
    W, H = 1100, 660
    v = Svg()

    v.add("<defs>")
    v.add(f'<linearGradient id="bg" x1="0" y1="0" x2="0.3" y2="1">'
          f'<stop offset="0" stop-color="{s["bg_from"]}"/>'
          f'<stop offset="1" stop-color="{s["bg_to"]}"/></linearGradient>')
    v.add(f'<filter id="soft" x="-30%" y="-30%" width="160%" height="170%">'
          f'<feDropShadow dx="0" dy="7" stdDeviation="9" '
          f'flood-color="{s["shadow_color"]}" flood-opacity="{s["shadow"]}"/></filter>')
    v.add('<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" '
          'markerWidth="6.4" markerHeight="6.4" orient="auto-start-reverse">'
          f'<path d="M0 0 L10 5 L0 10 z" fill="{s["accent"]}"/></marker>')
    v.add("</defs>")
    v.add(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')

    # ---- header -------------------------------------------------------------
    v.text(44, 50, "dsh-soilwater-check", 27, s["text"], weight=700, mono=True,
           max_w=330)
    title_w = measure("dsh-soilwater-check", 27, "mono_bold")
    tool_w = v.tag(44 + title_w + 14, 30, "soilwater_check", "", fg=s["accent"],
                   bg=s["band"], h=22)
    if 44 + title_w + 14 + tool_w > 1040:
        v.overflows.append("header tool chip exceeds the canvas")
    v.text(44, 78,
           "soilwater_check 读一份台账，按三种作用域核对；差异回到行号与栏名，未执行的逐条说明。",
           14, s["sub"], max_w=660)
    badge_id = "v2026.1"
    badge_gloss = "8 条 · 全部 warn"
    badge_w = (24 + measure(badge_id, 13, "mono_bold") + 8
               + measure(badge_gloss, 11, "cjk"))
    badge_x = 1056 - badge_w
    if badge_x < 700:
        v.overflows.append("header badge overlaps the subtitle")
    v.tag(badge_x, 30, badge_id, badge_gloss, fg=s["accent"], bg=s["band"], h=26)
    v.line(44, 92, 1056, 92, stroke=s["rule"], sw=1)

    # ---- view 1: the header row --------------------------------------------
    v.rect(44, 104, 672, 88, fill=s["panel"], rx=20, stroke=s["edge"], sw=1.5,
           shadow=True)
    v.circle(64, 128, 11, fill=s["accent"])
    v.text(64, 132, "1", 12, "#ffffff" if skin == "light" else "#111827",
           anchor="middle", weight=700, mono=True, max_w=14)
    v.text(84, 114, "表头", 13.5, s["text"], weight=700, max_w=110)
    v.text(84, 134, "header", 11, s["faint"], mono=True, max_w=110)
    v.text(84, 158, "JSON / YAML · 别名归一", 11, s["faint"], max_w=126)

    x = 214
    for key, gloss in (("project", "项目名称"), ("phase", "监测阶段")):
        w = v.kv_chip(x, 112, key, gloss, fg=s["text"], bg=s["band"])
        x += w + 10
    v.kv_chip(214, 144, "checkedAt", "核对日期", fg=s["text"], bg=s["band"])
    if x > 512:
        v.overflows.append(f"header key chips end at {x:.0f}, SW-007 card starts at 520")

    v.rect(520, 112, 180, 72, fill=s["band"], rx=14)
    v.text(532, 128, "SW-007", 13, s["text"], mono=True, weight=700, max_w=55)
    v.text(532, 148, "headerPresence", 11, s["sub"], mono=True, max_w=150)
    v.text(532, 166, "project + phase", 11, s["sub"], mono=True, max_w=150)
    v.badge(700 - measure("warn", 11, "mono_bold") - 20 - 12, 118, "warn",
            fg=s["amber"], bg=s["amber_bg"], h=20, size=11)

    # ---- view 2: one row, its cells and the five rules that read them ------
    v.rect(44, 204, 672, 188, fill=s["panel"], rx=20, stroke=s["edge"], sw=1.5,
           shadow=True)
    v.circle(64, 228, 11, fill=s["accent"])
    v.text(64, 232, "2", 12, "#ffffff" if skin == "light" else "#111827",
           anchor="middle", weight=700, mono=True, max_w=14)
    v.text(84, 214, "单行 × 栏", 13.5, s["text"], weight=700, max_w=140)
    v.text(84, 234, "row · 一条记录 = 点位 × 监测项目", 11, s["faint"],
           max_w=300)

    cells = [
        (60, 110, "点位名称", "S1 表层土", False),
        (176, 100, "监测项目", "砷", False),
        (282, 100, "监测结果", "80", True),
        (388, 128, "采样日期", "2026-03-05", True),
        (522, 170, "执行标准", "GB 36600—2018", True),
    ]
    for cx, cw, label, value, mono_value in cells:
        v.cell(cx, 258, cw, 60, label, value, s=s, mono_value=mono_value)

    tags = [
        ("SW-001", "点位|项目"),
        ("SW-008", "占位符"),
        ("SW-002", "数值"),
        ("SW-003", "日期"),
        ("SW-004", "标准"),
    ]
    x = 60
    for rid, gloss in tags:
        w = v.tag(x, 330, rid, gloss, fg=s["accent"], bg=s["band"])
        x += w + 10
    if x > 704:
        v.overflows.append(f"row rule chips end at {x:.0f} > 704")

    v.text(60, 374,
           "列名按台账自己的写法；别名归一到 canonical 字段（忽略大小写、空格、下划线）。",
           11, s["faint"], max_w=632)

    # ---- view 3: the column and the three-cell relation --------------------
    v.rect(44, 404, 672, 136, fill=s["panel"], rx=20, stroke=s["edge"], sw=1.5,
           shadow=True)
    v.circle(64, 428, 11, fill=s["accent"])
    v.text(64, 432, "3", 12, "#ffffff" if skin == "light" else "#111827",
           anchor="middle", weight=700, mono=True, max_w=14)
    v.text(84, 414, "跨行 · 跨栏", 13.5, s["text"], weight=700, max_w=160)
    v.text(84, 434, "column · 一栏看全表，三栏一起看", 11, s["faint"],
           max_w=300)

    # left: the lab-number column, twice the same value
    v.text(60, 454, "样品编号 labNo", 11, s["faint"], max_w=120)
    v.cell(60, 462, 106, 28, "", "TR-2026-0018", s=s, mono_value=True,
           accent=s["amber"])
    v.cell(60, 496, 106, 28, "", "TR-2026-0018", s=s, mono_value=True,
           accent=s["amber"])
    v.line(172, 466, 172, 520, stroke=s["amber"], sw=1.6, opacity=0.6)
    v.line(166, 466, 172, 466, stroke=s["amber"], sw=1.6, opacity=0.6)
    v.line(166, 520, 172, 520, stroke=s["amber"], sw=1.6, opacity=0.6)
    v.tag(180, 464, "SW-006", "unique", fg=s["amber"], bg=s["amber_bg"], h=24)
    v.text(180, 500, "重复 → issue", 11, s["amber"], max_w=110)
    v.text(180, 518, "比较时忽略空白", 11, s["faint"], max_w=120)

    # right: result × limit × verdict
    v.text(320, 454, "SW-005 三栏联动", 11, s["faint"], max_w=160)
    v.text(470, 454, "thresholdCompare", 11, s["faint"], mono=True, max_w=180)
    v.cell(320, 464, 74, 30, "结果", "80", s=s, mono_value=True)
    v.text(402, 486, ">", 13, s["accent"], anchor="middle", weight=700,
           mono=True, max_w=12)
    v.cell(414, 464, 74, 30, "限值", "60", s=s, mono_value=True)
    v.line(494, 479, 514, 479, stroke=s["accent"], sw=1.6, marker="arr")
    v.rect(522, 464, 178, 30, fill=s["amber_bg"], rx=9,
           stroke=s["amber"], sw=1.6)
    v.text(532, 476, "80 > 60", 11, s["amber"], mono=True, weight=700, max_w=60)
    v.text(590, 476, "应判「超标」", 11, s["amber"], max_w=100)

    v.cell(320, 500, 74, 30, "判定", "达标", s=s, accent=s["amber"])
    v.circle(408, 515, 9, fill=s["amber_bg"], stroke=s["amber"], sw=1.8)
    v.path("M404 511 L412 519", stroke=s["amber"], sw=2)
    v.path("M412 511 L404 519", stroke=s["amber"], sw=2)
    v.text(424, 506, "「达标」与两数关系不符", 11.5, s["amber"], max_w=220)
    v.text(424, 522, "第 1 行 · field exceed", 11, s["faint"],
           max_w=220)

    # ---- control surface: evidence → severity, citation gap, config --------
    v.rect(732, 104, 324, 436, fill=s["card"], rx=20, stroke=s["edge"], sw=1.5,
           shadow=True)
    v.text(752, 128, "证据 → 严重级", 15, s["text"], weight=700, max_w=284)
    v.text(752, 148, "severity follows the evidence", 11, s["faint"],
           mono=True, max_w=284)

    basis_rows = [
        ("direct", "条款直接规定", "error", s["accent2"]),
        ("derived-from-principle", "仅能由原则推论", "warn", s["amber"]),
        ("institutional-configuration", "本机构配置阈值", "info", s["sub"]),
    ]
    y = 170
    for kind, gloss, cap, color in basis_rows:
        v.text(752, y, kind, 12, s["text"], mono=True, weight=700, max_w=212)
        v.text(752, y + 18, gloss, 11, s["sub"], max_w=212)
        v.rect(966, y - 10, 70, 20, fill=s["band"], rx=10)
        v.text(1001, y + 4, f"<= {cap}", 11, color, mono=True, anchor="middle",
               max_w=64)
        y += 42

    v.line(752, 300, 1036, 300, stroke=s["rule"], sw=1)
    v.text(752, 322, "本包 · 8/8 无逐字引文", 13, s["text"], weight=700,
           max_w=284)
    v.text(752, 344, "每条 excerpt 写明「本次未取得」；", 11, s["sub"],
           max_w=284)
    v.text(752, 362, "kind = derived-from-principle", 11, s["sub"],
           mono=True, max_w=284)
    v.text(752, 380, "severity 封顶 warn；取得原文后再换 direct。", 11,
           s["sub"], max_w=284)

    v.line(752, 398, 1036, 398, stroke=s["rule"], sw=1)
    v.text(752, 420, "config", 13, s["text"], weight=700, mono=True, max_w=284)
    for index, (key, gloss) in enumerate((
            ("rulesFile", "换规则包即换整套检查"),
            ("disabledRules / onlyRules", "停用 / 只跑"),
            ("skipNotes / timeoutMs", "skipped 备注 / 超时预算"))):
        v.text(752, 440 + index * 28, key, 11, s["accent"], mono=True,
               max_w=284)
        v.text(752, 456 + index * 28, gloss, 11, s["faint"], max_w=284)

    # ---- report band: issues[] + skipped[] → reviewer ----------------------
    v.rect(44, 552, 1012, 70, fill=s["panel"], rx=20, stroke=s["edge"], sw=1.5,
           shadow=True)
    v.line(572, 564, 572, 610, stroke=s["rule"], sw=1)
    v.line(924, 564, 924, 610, stroke=s["rule"], sw=1)

    v.text(60, 570, "issues[]", 13, s["accent"], mono=True, weight=700,
           max_w=70)
    v.rect(122, 558, 84, 18, fill=s["band"], rx=9)
    v.text(164, 571, "2 条 · warn", 10.5, s["amber"], anchor="middle",
           max_w=78)
    v.text(60, 590,
           "SW-005：80 > 60 却判「达标」；SW-006：两行共用同一编号",
           11, s["text"], max_w=490)
    v.text(60, 608, "每条带 ruleId · locator{row, field} · found · expected · fix",
           11, s["faint"], mono=True, max_w=490)

    v.text(588, 570, "skipped[]", 13, s["sub"], mono=True, weight=700,
           max_w=90)
    v.rect(672, 558, 46, 18, fill=s["band"], rx=9)
    v.text(695, 571, "0 条", 10.5, s["sub"], anchor="middle", max_w=40)
    v.text(588, 590, "disabled / only / 缺列 / 空清单 → 逐条写原因", 11,
           s["text"], max_w=320)
    v.text(588, 608, "空 issues ≠ 没问题：两条通道一起读", 11, s["faint"],
           max_w=320)

    v.text(940, 570, "审核人", 13.5, s["text"], weight=700, max_w=100)
    v.text(940, 592, "结论不在报告里", 11, s["sub"], max_w=100)
    v.text(940, 610, "只列差异", 11, s["faint"], max_w=100)

    # ---- left collector: three scopes converge on the one report -----------
    v.line(44, 148, 28, 148, stroke=s["accent"], sw=1.5, opacity=0.55)
    v.line(44, 298, 28, 298, stroke=s["accent"], sw=1.5, opacity=0.55)
    v.line(44, 472, 28, 472, stroke=s["accent"], sw=1.5, opacity=0.55)
    v.line(28, 148, 28, 580, stroke=s["accent"], sw=1.5, opacity=0.55)
    v.line(28, 580, 42, 580, stroke=s["accent"], sw=1.5, opacity=0.55,
           marker="arr")
    for junction in (148, 298, 472):
        v.circle(28, junction, 2.4, fill=s["accent"])

    # ---- footer -------------------------------------------------------------
    v.text(44, 638,
           "SW-005 只按台账自己写的限值比较，不判断限值是否取自正确的标准；空 issues ≠ 没问题。",
           11, s["sub"], max_w=820)
    v.text(44, 652,
           "示例值取自 tests/fixtures/SW-005-unsafe.json 与 SW-006-unsafe.json ｜ 只读材料 · 不联网 · 不调用模型",
           11, s["faint"], max_w=820)
    v.text(1056, 652, "Apache-2.0 · PerryLink DSH plugin family", 11,
           s["faint"], anchor="end", max_w=260)

    if v.overflows:
        raise SystemExit("FATAL: SVG label overflow:\n  " + "\n  ".join(v.overflows))
    return v.svg(
        W, H,
        "dsh-soilwater-check 结构图：一份台账按三种作用域核对——表头 SW-007、"
        "单行×栏 SW-001/002/003/004/008、跨行·跨栏 SW-006 与 SW-005；"
        "差异回到行号与栏名，一条 issues[] 与 skipped[] 通道汇入报告，结论留给审核人")


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for skin in ("light", "dark"):
        for lang in ("zh", "en"):
            hero(lang, skin)
        name = f"dsh-soilwater-check-flow-v5-{skin}.svg"
        with open(os.path.join(OUT, name), "w", encoding="utf-8",
                  newline="\n") as fh:
            fh.write(flow_svg(skin))
        print(f"wrote {name} (1100×660)")


if __name__ == "__main__":
    main()
