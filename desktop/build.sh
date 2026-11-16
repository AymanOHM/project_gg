#!/usr/bin/env bash
# Build a standalone desktop version of the game with PyInstaller.
#
#   ./desktop/build.sh      result in dist/ProjectGG/ (run dist/ProjectGG/ProjectGG)
#
# PyInstaller cannot cross-compile: run this on the system you are building for.
# The game finds its assets relative to the gg_client package, and inside the
# bundle that is the bundle's own folder, so the data only has to be copied in
# at the same relative paths.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

data_args=(--add-data "data/levels:data/levels" --add-data "data/sfx:data/sfx" --add-data "data/music.ogg:data")
for folder in tiles clouds entities/player entities/player2; do
  data_args+=(--add-data "data/images/$folder:data/images/$folder")
done
for image in _gun bullet3 health_simple P1 P2; do
  data_args+=(--add-data "data/images/$image.png:data/images")
done

# Paths stay relative to the repo root (where the .spec file is written). Absolute
# paths from Git Bash on Windows look like /d/a/..., which PyInstaller cannot read.
uv run --group desktop pyinstaller --noconfirm --clean --windowed --name ProjectGG \
  --distpath dist --workpath build/pyinstaller --specpath . \
  --paths . "${data_args[@]}" desktop/main.py
