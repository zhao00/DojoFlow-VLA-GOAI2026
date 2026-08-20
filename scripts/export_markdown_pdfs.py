#!/usr/bin/env python3
"""Render repository Markdown files to a separate, mirrored PDF tree.

Inline ``$...$`` and display ``$$...$$`` LaTeX are converted to embedded SVG
before Markdown parsing.  This keeps subscripts, superscripts and mathematical
symbols stable in WeasyPrint without JavaScript or a network-loaded MathJax
bundle.
"""

from __future__ import annotations

import argparse
import base64
import html
import re
from io import BytesIO
from pathlib import Path

import markdown
from matplotlib.mathtext import math_to_image
from weasyprint import CSS, HTML


CSS_TEXT = r"""
@page {
  size: A4;
  margin: 18mm 17mm 18mm 17mm;
  @bottom-center {
    content: counter(page) " / " counter(pages);
    color: #64748b;
    font-size: 9pt;
  }
}
html { font-family: "Noto Sans CJK SC", "Noto Sans CJK", sans-serif; }
body { color: #172033; font-size: 10.5pt; line-height: 1.68; }
h1, h2, h3, h4 { color: #123b68; line-height: 1.35; page-break-after: avoid; }
h1 { font-size: 23pt; border-bottom: 2px solid #2d6caa; padding-bottom: 5mm; }
h2 { font-size: 16pt; border-bottom: 1px solid #cbd5e1; padding-bottom: 1.5mm; }
h3 { font-size: 12.5pt; }
p, li { orphans: 3; widows: 3; }
a { color: #155e9a; text-decoration: none; overflow-wrap: anywhere; }
table { width: 100%; border-collapse: collapse; margin: 4mm 0; font-size: 9pt; }
thead { display: table-header-group; }
tr { page-break-inside: avoid; }
th { background: #245d96; color: white; font-weight: 600; }
th, td { border: 0.35mm solid #9aa9b8; padding: 2mm; vertical-align: top; }
tbody tr:nth-child(even) { background: #f4f7fa; }
code { font-family: "Noto Sans Mono CJK SC", "DejaVu Sans Mono", monospace; }
code:not(pre code) { background: #eef2f6; padding: 0.2mm 1mm; border-radius: 1mm; }
pre { background: #111827; color: #e5edf6; padding: 3mm; border-radius: 1.5mm;
      white-space: pre-wrap; overflow-wrap: anywhere; font-size: 8.5pt; }
blockquote { border-left: 1.2mm solid #4d83b7; margin-left: 0; padding-left: 4mm; color: #475569; }
img { max-width: 100%; height: auto; page-break-inside: avoid; }
img.math-inline { display: inline-block; max-width: none; width: auto;
                  height: 1.15em; margin: 0 0.06em; vertical-align: -0.25em; }
.math-block { display: block; margin: 4mm 0; text-align: center;
              page-break-inside: avoid; }
.math-block img { display: inline-block; width: auto; max-width: 95%; height: auto; }
hr { border: 0; border-top: 0.3mm solid #cbd5e1; }
.source-note { margin-top: 8mm; color: #64748b; font-size: 8pt; }
"""


def first_title(text: str, fallback: str) -> str:
    match = re.search(r"^#\s+(.+?)\s*$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else fallback


def render_math_svg(latex: str, block: bool) -> str:
    """Render a LaTeX fragment to a self-contained SVG data URI."""

    # Matplotlib MathText spells paired norm delimiters as \Vert.  Normalizing
    # the LaTeX aliases preserves the intended scalable double bars.
    normalized = latex.replace(r"\lVert", r"\left\Vert").replace(
        r"\rVert", r"\right\Vert"
    )
    buffer = BytesIO()
    math_to_image(
        f"${normalized}$",
        buffer,
        format="svg",
        dpi=144,
        color="#172033",
    )
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    alt = html.escape(latex, quote=True)
    image = f'<img src="data:image/svg+xml;base64,{encoded}" alt="{alt}">'
    if block:
        return f'<div class="math-block">{image}</div>'
    return image.replace("<img ", '<img class="math-inline" ', 1)


def protect_math(text: str) -> tuple[str, dict[str, tuple[str, bool]]]:
    """Replace LaTeX delimiters with Markdown-safe tokens.

    Block formulas are protected first, then single-line inline formulas.  The
    returned mapping stores already rendered SVG HTML and whether the formula is
    block-level.  This repository uses dollar delimiters only for mathematics;
    escaped dollars remain untouched.
    """

    formulas: dict[str, tuple[str, bool]] = {}

    def token(rendered: str, block: bool) -> str:
        marker = f"DOJOFLOWMATHPLACEHOLDER{len(formulas):04d}END"
        formulas[marker] = (rendered, block)
        return marker

    def replace_block(match: re.Match[str]) -> str:
        latex = match.group(1).strip()
        return "\n\n" + token(render_math_svg(latex, True), True) + "\n\n"

    def replace_inline(match: re.Match[str]) -> str:
        latex = match.group(1).strip()
        return token(render_math_svg(latex, False), False)

    protected = re.sub(
        r"(?<!\\)\$\$(.+?)(?<!\\)\$\$",
        replace_block,
        text,
        flags=re.DOTALL,
    )
    protected = re.sub(
        r"(?<!\\)\$(?!\$)([^\n$]+?)(?<!\\)\$",
        replace_inline,
        protected,
    )
    return protected, formulas


def restore_math(body: str, formulas: dict[str, tuple[str, bool]]) -> str:
    """Replace protected tokens in generated HTML with rendered SVG markup."""

    for marker, (rendered, block) in formulas.items():
        if block:
            body, count = re.subn(
                rf"<p>\s*{re.escape(marker)}\s*</p>",
                lambda _: rendered,
                body,
            )
            if count != 1:
                raise ValueError(f"block formula placeholder was not preserved: {marker}")
        else:
            if body.count(marker) != 1:
                raise ValueError(f"inline formula placeholder was not preserved: {marker}")
            body = body.replace(marker, rendered)
    return body


def render_one(source: Path, destination: Path, source_root: Path) -> None:
    md_text = source.read_text(encoding="utf-8")
    title = first_title(md_text, source.stem)
    protected_text, formulas = protect_math(md_text)
    body = markdown.markdown(
        protected_text,
        extensions=["extra", "sane_lists", "toc"],
        output_format="html5",
    )
    body = restore_math(body, formulas)

    # The output directory mirrors the source tree, so Markdown document links
    # can point to their generated PDF counterparts.
    body = re.sub(
        r'href="([^"#:?]+)\.md(#[^"]*)?"',
        lambda m: f'href="{m.group(1)}.pdf{m.group(2) or ""}"',
        body,
    )

    relative_source = source.relative_to(source_root).as_posix()
    document = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>{html.escape(title)}</title>
</head>
<body>
{body}
<p class="source-note">源文件：{html.escape(relative_source)}</p>
</body>
</html>
"""

    destination.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=document, base_url=str(source.parent)).write_pdf(
        str(destination), stylesheets=[CSS(string=CSS_TEXT)]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_root", type=Path)
    parser.add_argument("output_root", type=Path)
    args = parser.parse_args()

    source_root = args.source_root.resolve()
    output_root = args.output_root.resolve()
    if source_root == output_root or source_root in output_root.parents:
        raise SystemExit("output_root must be outside source_root")

    sources = sorted(
        path
        for path in source_root.rglob("*.md")
        if ".git" not in path.parts
    )
    if not sources:
        raise SystemExit(f"no Markdown files under {source_root}")

    for source in sources:
        relative = source.relative_to(source_root).with_suffix(".pdf")
        destination = output_root / relative
        render_one(source, destination, source_root)
        print(f"{relative.as_posix()}")

    print(f"generated={len(sources)} output={output_root}")


if __name__ == "__main__":
    main()
