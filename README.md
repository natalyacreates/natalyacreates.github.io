# Natalya's Quilts — gallery site

A modern, low-scroll gallery for natalyacreates.github.io. Quilts are grouped by
their letter prefix (A1, A2 -> "Collection A"; B1 -> "Collection B"), shown one
collection at a time via tabs, with a full-size detail view (title + description)
on click.

## Repository layout
    natalyacreates.github.io/      <- the repo (named to match the org)
        index.html
        quilts.js                  <- auto-generated; don't edit by hand
        generate_gallery.py
        captions.csv               <- optional (titles/descriptions)
        images/                    <- all photos go here
            A1.jpg, A2.jpg, B1.jpg, ...

## Photo & video rules
- Name them letter-then-number: A1.jpg, A2.jpg, B10.jpg.
- Images: JPG, PNG, GIF, WEBP, AVIF. iPhone .HEIC won't show in browsers —
  export those as JPEG (the script lists any it finds).
- Video: MP4 (H.264) and WEBM display and play, with controls, right in the
  gallery. A video tile shows a play badge; clicking it opens a player.
  .MOV / .AVI / .MKV may not play in all browsers — convert to MP4 first
  (the script flags any it finds). Keep clips small; GitHub rejects files
  over 100 MB and Pages has a monthly bandwidth limit.

## Optional: real titles & descriptions
Rename captions.example.csv to captions.csv and fill in three columns:
`filename,title,description`. Use the filename with or without its extension
(A1 or A1.jpg). Missing rows just fall back to a label like "A 1".

## Build the gallery
From inside the repo folder (the one with index.html):

    python3 generate_gallery.py

It scans images/ and writes quilts.js. Re-run any time you add photos or edit
captions. Double-click index.html to preview locally.

## Deploy to natalyacreates.github.io

### 1. Name the repo correctly
For the site to live at the root `https://natalyacreates.github.io/`, the repo
must be named exactly `natalyacreates.github.io` (all lowercase). If it's
currently named `natalyacreates`, rename it: repo Settings -> General ->
Repository name. (Leaving it as `natalyacreates` instead serves the site at
`natalyacreates.github.io/natalyacreates/`.) Make sure the repo is Public.

### 2. Put the files in and push
Clone the repo, add the gallery, and push:

    git clone https://github.com/natalyacreates/natalyacreates.github.io.git
    cd natalyacreates.github.io

    mkdir -p images
    cp /Users/davesumner/QUILT_PHOTOS/*.jpg images/      # copy your photos in
    # (also copy *.png / *.jpeg if you have them)

    # copy in the gallery files (adjust the source path):
    cp ~/Downloads/quilt-site/index.html .
    cp ~/Downloads/quilt-site/generate_gallery.py .
    cp ~/Downloads/quilt-site/captions.example.csv .     # optional

    python3 generate_gallery.py

    git add .
    git commit -m "Add quilt gallery"
    git branch -M main
    git push -u origin main

### 3. Turn on Pages
Repo Settings -> Pages. Under "Build and deployment" set Source to
"Deploy from a branch", Branch `main`, Folder `/ (root)`, Save. Give it a minute,
then open https://natalyacreates.github.io/ . (A `<org>.github.io` repo often
enables this automatically once content is pushed.)

### 4. Point the Format menu at it
On nescreates.com (Format): Portfolio -> Pages -> add an external Link titled
"Quilt Gallery" pointing to https://natalyacreates.github.io/ , set to open in
the same tab, and unpublish the old internal gallery.

## Notes
- A robots.txt (to opt out of AI training crawlers) only works at a domain root,
  which the `natalyacreates.github.io` repo gives you. Ask and I'll generate one.
- Updating later: drop new photos in images/, run the script, then
  `git add . && git commit -m "..." && git push`.
