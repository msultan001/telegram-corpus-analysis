#!/usr/bin/env python3
"""Convert Markdown to PDF.

Strategy:
- Try `pandoc input.md -o output.pdf`.
- If pandoc is unavailable, fall back to writing plain text into a PDF using reportlab.

Usage: python scripts/md_to_pdf.py reports/interim_report.md reports/interim_report.pdf
"""
import sys
import subprocess
from pathlib import Path


def try_pandoc(src: Path, dst: Path) -> bool:
    try:
        res = subprocess.run(["pandoc", str(src), "-o", str(dst)], check=False, capture_output=True)
        if res.returncode == 0:
            print("pandoc conversion succeeded")
            return True
        else:
            print("pandoc failed:", res.stderr.decode(errors='ignore'))
            return False
    except FileNotFoundError:
        print("pandoc not found")
        return False


def fallback_reportlab(src: Path, dst: Path) -> bool:
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except Exception:
        print("reportlab not installed, attempting to install...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])  # may fail
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
        except Exception as e:
            print("Failed to import reportlab after install:", e)
            return False

    text = src.read_text(encoding="utf-8")
    lines = text.splitlines()

    c = canvas.Canvas(str(dst), pagesize=letter)
    width, height = letter
    margin = 40
    y = height - margin
    line_height = 12

    def write_line(s):
        nonlocal y
        if y < margin + line_height:
            c.showPage()
            y = height - margin
        c.drawString(margin, y, s)
        y -= line_height

    # Very basic rendering: headings and pre blocks preserved as plain text
    for ln in lines:
        if ln.strip() == "":
            write_line("")
            continue
        # render code fence lines verbatim
        if ln.startswith("```"):
            write_line(ln)
            continue
        # headings: make uppercase
        if ln.startswith("#"):
            write_line(ln.lstrip("#").strip().upper())
            continue
        # wrap long lines simply
        if len(ln) > 90:
            for i in range(0, len(ln), 90):
                write_line(ln[i : i + 90])
        else:
            write_line(ln)

    c.save()
    print("reportlab fallback PDF written")
    return True


def main(argv):
    if len(argv) < 3:
        print("Usage: md_to_pdf.py input.md output.pdf")
        return 2

    src = Path(argv[1])
    dst = Path(argv[2])
    if not src.exists():
        print("Input file not found:", src)
        return 3

    if try_pandoc(src, dst):
        return 0

    ok = fallback_reportlab(src, dst)
    return 0 if ok else 4


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
