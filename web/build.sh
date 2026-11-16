#!/usr/bin/env bash
# Build the browser version of the game with pygbag.
#
#   ./web/build.sh           build into build/web-app/build/web
#   ./web/build.sh --serve   build, then serve on http://localhost:8000
#
# pygbag packages one folder, so this stages the code and only the assets the
# game loads into build/web-app first.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
app="$root/build/web-app"

rm -rf "$app"
mkdir -p "$app/data/images/entities"
cp "$root/web/main.py" "$app/main.py"
cp -R "$root/gg_core" "$root/gg_client" "$app/"
cp -R "$root/data/levels" "$app/data/levels"
cp -R "$root/data/sfx" "$app/data/sfx"
cp "$root/data/music.ogg" "$app/data/music.ogg"
cp -R "$root/data/images/tiles" "$root/data/images/clouds" "$app/data/images/"
cp -R "$root/data/images/entities/player" "$root/data/images/entities/player2" "$app/data/images/entities/"
for image in _gun bullet3 health_simple P1 P2; do
  cp "$root/data/images/$image.png" "$app/data/images/"
done
find "$app" -name __pycache__ -type d -prune -exec rm -rf {} +

cd "$root"
if [ "${1:-}" = "--serve" ]; then
  exec uv run --group web pygbag --title "Project GG" "$app"
fi
uv run --group web pygbag --build --title "Project GG" "$app"
du -sh "$app/build/web"/*
