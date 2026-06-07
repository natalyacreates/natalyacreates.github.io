#!/usr/bin/env python3
"""
generate_gallery.py
-------------------
Scans your quilt photos, groups them by their letter prefix
(A1, A2, A3 -> "A";  B1, B2 -> "B"), sorts each group numerically,
and writes quilts.js for the gallery to read.

WHERE TO PUT PHOTOS
    Preferred: a subfolder called  images/  next to index.html.
        your-repo/
            index.html
            generate_gallery.py
            images/
                A1.jpg, A2.jpg, B1.jpg, ...
    If there is no images/ folder, the script falls back to scanning the
    current folder (photos sitting next to index.html).

USAGE
    Run it from the folder that holds index.html:

        python3 generate_gallery.py

    Filenames must be a letter (or letters) then a number: A1.jpg, B10.jpg.
    Anything else is reported and skipped.

OPTIONAL TITLES & DESCRIPTIONS
    Put a  captions.csv  next to index.html with three columns:

        filename,title,description
        A1.jpg,Inner Light,"Art quilt featuring a silhouette..."

    A header row is optional; the filename may include the extension or not
    (A1 or A1.jpg). Quilts with no row fall back to a label like "A 1".
"""

import os
import re
import sys
import csv
import json

WEB_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif"}
VIDEO_EXTS = {".mp4", ".webm"}
# Formats browsers can't display directly -> warn the user to convert.
SKIP_EXTS = {".heic", ".heif", ".tif", ".tiff", ".cr2", ".nef", ".dng", ".arw"}
VIDEO_CONVERT = {".mov", ".avi", ".mkv", ".m4v", ".wmv"}

# collection_prefix_number, e.g. available_work_01.jpg
# Everything before the last _number is the collection name.
PATTERN = re.compile(r"^(.+)_0*(\d+)$")

# preferred photo subfolder
PHOTO_SUBDIR = "images"

# our own files, never treated as photos (only relevant in the flat fallback)
IGNORE = {"index.html", "quilts.js", "generate_gallery.py", "README.md",
          "captions.csv", "robots.txt"}


def load_captions(folder):
    """Return {normalized_name: (title, description)} from captions.csv, if present."""
    path = os.path.join(folder, "captions.csv")
    captions = {}
    if not os.path.isfile(path):
        return captions
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    for i, row in enumerate(rows):
        if not row or not row[0].strip():
            continue
        first = row[0].strip().lower()
        if i == 0 and first in ("filename", "file", "name"):
            continue  # skip an optional header row
        name = row[0].strip()
        title = row[1].strip() if len(row) > 1 else ""
        desc = row[2].strip() if len(row) > 2 else ""
        captions[name.lower()] = (title, desc)
        captions[os.path.splitext(name)[0].lower()] = (title, desc)
    return captions


def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else "."
    folder = os.path.abspath(folder)

    if not os.path.isdir(folder):
        print(f"  Folder not found: {folder}")
        sys.exit(1)

    # photos live in images/ if it exists, otherwise alongside index.html
    sub = os.path.join(folder, PHOTO_SUBDIR)
    if os.path.isdir(sub):
        scan_dir = sub
        url_prefix = PHOTO_SUBDIR + "/"
    else:
        scan_dir = folder
        url_prefix = ""

    captions = load_captions(folder)

    groups = {}      # { "A": [(num, filename), ...] }
    unmatched = []
    needs_convert = []
    video_convert = []

    for name in os.listdir(scan_dir):
        if name.startswith("."):
            continue
        if url_prefix == "" and name in IGNORE:
            continue
        if not os.path.isfile(os.path.join(scan_dir, name)):
            continue

        ext = os.path.splitext(name)[1].lower()
        if ext in SKIP_EXTS:
            needs_convert.append(name)
            continue
        if ext in VIDEO_CONVERT:
            video_convert.append(name)
            continue
        if ext not in WEB_EXTS and ext not in VIDEO_EXTS:
            continue

        stem = os.path.splitext(name)[0]
        m = PATTERN.match(stem)
        if not m:
            unmatched.append(name)
            continue

        collection = m.group(1)          # e.g. "available_work"
        number = int(m.group(2))
        groups.setdefault(collection, []).append((number, name))

    if not groups:
        print("  No photos matched the expected naming pattern.")
        print("  Files should be named:  collection_name_01.jpg")
        print("  Example: available_work_01.jpg, commissions_03.jpg")
        if needs_convert:
            print("  (Found files that browsers can't show; see note below.)")

    # sort: collections alphabetically, photos within each collection by number
    ordered = {}
    caption_hits = 0
    for collection in sorted(groups):
        photos = sorted(groups[collection], key=lambda t: (t[0], t[1]))
        items = []
        for _, name in photos:
            stem_lower = os.path.splitext(name)[0].lower()
            title, desc = captions.get(name.lower(), captions.get(stem_lower, ("", "")))
            if title or desc:
                caption_hits += 1
            kind = "video" if os.path.splitext(name)[1].lower() in VIDEO_EXTS else "image"
            items.append({"file": url_prefix + name, "type": kind,
                          "title": title, "desc": desc})
        ordered[collection] = items

    # write quilts.js next to index.html (repo root), not in images/
    out = os.path.join(folder, "quilts.js")
    payload = json.dumps(ordered, indent=2, ensure_ascii=False)
    with open(out, "w", encoding="utf-8") as f:
        f.write("// Auto-generated by generate_gallery.py. Re-run the script to update.\n")
        f.write("window.QUILTS = " + payload + ";\n")

    # report
    where = os.path.relpath(scan_dir, folder)
    where = "images/" if where == PHOTO_SUBDIR else "this folder"
    print("\n  Quilt gallery generated\n  " + "-" * 38)
    print(f"  Scanned photos in: {where}")
    total = 0
    for collection, items in ordered.items():
        total += len(items)
        print(f"  {collection}: {len(items)} photo(s)")
    print("  " + "-" * 38)
    print(f"  {total} photo(s) across {len(ordered)} collection(s)")
    if captions:
        print(f"  {caption_hits} photo(s) matched a title/description in captions.csv")
    else:
        print("  No captions.csv found (optional - see notes in this script).")
    print(f"  Wrote: {out}\n")

    if unmatched:
        print("  Skipped (no  collection_name_number  pattern found):")
        for n in sorted(unmatched):
            print(f"      - {n}")
        print()
    if needs_convert:
        print("  These images can't be shown by web browsers - export them as JPEG first:")
        for n in sorted(needs_convert):
            print(f"      - {n}")
        print()
    if video_convert:
        print("  These videos may not play in all browsers - convert to MP4 (H.264) first:")
        for n in sorted(video_convert):
            print(f"      - {n}")
        print()

    print("  Next: commit and push, then check https://natalyacreates.github.io/")
    print("  See README.md for the full deploy steps.\n")


if __name__ == "__main__":
    main()
