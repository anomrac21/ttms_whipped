#!/usr/bin/env python3
"""Download section images (Pexels) and update content/*/_index.md."""
from __future__ import annotations

import re
import urllib.error
import urllib.request
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
IMAGES_DIR = ROOT / "static" / "images"

PEX = "https://images.pexels.com/photos/{id}/pexels-photo-{id}.jpeg?auto=compress&cs=tinysrgb&w=900"

PEXELS: dict[str, tuple[str, str]] = {
    "hero.webp": (PEX.format(id="1267325"), "Pexels #1267325"),
    "promotions.webp": (PEX.format(id="2233348"), "Pexels #2233348"),
    "soup.webp": (PEX.format(id="539451"), "Pexels #539451"),
    "salads.webp": (PEX.format(id="1128678"), "Pexels #1128678"),
    "oh-crepe.webp": (PEX.format(id="1893556"), "Pexels #1893556"),
    "rice-bowls.webp": (PEX.format(id="1279330"), "Pexels #1279330"),
    "pasta.webp": (PEX.format(id="2097090"), "Pexels #2097090"),
    "tapas.webp": (PEX.format(id="248444"), "Pexels #248444"),
    "mains.webp": (PEX.format(id="3535384"), "Pexels #3535384"),
    "sliders.webp": (PEX.format(id="769289"), "Pexels #769289"),
    "sides.webp": (PEX.format(id="410648"), "Pexels #410648"),
    "paninis-sandwiches.webp": (PEX.format(id="1630757"), "Pexels #1630757"),
    "slideshow-cocktail.webp": (PEX.format(id="274192"), "Pexels #274192"),
    "slideshow-pasta.webp": (PEX.format(id="2097090"), "Pexels #2097090"),
    "slideshow-mains.webp": (PEX.format(id="618785"), "Pexels #618785"),
}

SECTIONS: dict[str, str] = {
    "promotions": "promotions.webp",
    "soup": "soup.webp",
    "salads": "salads.webp",
    "oh-crepe": "oh-crepe.webp",
    "rice-bowls": "rice-bowls.webp",
    "pasta": "pasta.webp",
    "tapas": "tapas.webp",
    "mains": "mains.webp",
    "sliders": "sliders.webp",
    "sides": "sides.webp",
    "paninis-sandwiches": "paninis-sandwiches.webp",
}


def img(name: str) -> str:
    return f"images/{name}"


def download_pexels(filename: str, url: str) -> bool:
    from PIL import Image

    webp = IMAGES_DIR / filename
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
    except urllib.error.HTTPError as e:
        print(f"SKIP {filename}: HTTP {e.code}")
        return webp.exists()
    Image.open(BytesIO(data)).save(webp, "WEBP", quality=85)
    print(f"OK {filename}")
    return True


def body_after_frontmatter(raw: str) -> str:
    if raw.count("---") < 2:
        return raw.strip()
    return raw.split("---", 2)[2].strip()


def update_section_index(section: str, image_file: str) -> None:
    path = CONTENT / section / "_index.md"
    if not path.exists():
        return
    raw = path.read_text(encoding="utf-8")
    title_m = re.search(r"^title:\s*(.+)$", raw, re.M)
    weight_m = re.search(r"^weight:\s*(.+)$", raw, re.M)
    title = title_m.group(1).strip().strip('"') if title_m else section.replace("-", " ").title()
    weight = weight_m.group(1).strip().strip('"') if weight_m else "1"
    body = body_after_frontmatter(raw)

    lines = [
        "---",
        f"title: {title}",
        f"weight: {weight}",
        f"icon: {img(image_file)}",
        "images:",
        f"    primary: {img(image_file)}",
        "---",
    ]
    if body:
        lines.extend(["", body])
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def update_home_index() -> None:
    path = CONTENT / "_index.md"
    body = body_after_frontmatter(path.read_text(encoding="utf-8"))
    if not body.strip():
        body = (
            "<p>Whipped — National Restaurant, Hookah &amp; Cocktail Bar. "
            "One Woodbrook Place, Port of Spain.</p>"
        )
    text = (
        "---\n"
        'title: "Whipped"\n'
        f"image: {img('hero.webp')}\n"
        "images:\n"
        f"    - image: {img('hero.webp')}\n"
        f"    - image: {img('mains.webp')}\n"
        f"    - image: {img('tapas.webp')}\n"
        f"    - image: {img('pasta.webp')}\n"
        "slideshow:\n"
        f"    - image: {img('hero.webp')}\n"
        f"    - image: {img('slideshow-cocktail.webp')}\n"
        f"    - image: {img('slideshow-mains.webp')}\n"
        f"    - image: {img('slideshow-pasta.webp')}\n"
        f"    - image: {img('tapas.webp')}\n"
        f"    - image: {img('promotions.webp')}\n"
        "---"
    )
    text += f"\n\n{body}\n"
    path.write_text(text, encoding="utf-8")


def main() -> None:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    credits: list[str] = []

    for filename, (url, credit) in PEXELS.items():
        if download_pexels(filename, url):
            credits.append(f"- {filename} — {credit}")

    missing = [s for s, f in SECTIONS.items() if not (IMAGES_DIR / f).exists()]
    if missing:
        print("Missing:", ", ".join(missing))
        return

    for section, image_file in SECTIONS.items():
        update_section_index(section, image_file)

    if (IMAGES_DIR / "hero.webp").exists():
        update_home_index()

    (IMAGES_DIR / "IMAGE_CREDITS.txt").write_text(
        "Section photos (Pexels License — free to use):\n" + "\n".join(credits) + "\n",
        encoding="utf-8",
    )
    print("Section headers updated.")


if __name__ == "__main__":
    main()
