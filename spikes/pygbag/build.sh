#!/usr/bin/env bash
# Stage the assets the spike needs, then build the web bundle with pygbag.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
root="$(cd "$here/../.." && pwd)"

rm -rf "$here/data" "$here/build"
mkdir -p "$here/data/entities"
cp -R "$root/data/images/tiles" "$here/data/tiles"
cp -R "$root/data/images/entities/player" "$here/data/entities/player"
cp "$root/map.json" "$here/data/map.json"

[ "${1:-}" = "--assets-only" ] && exit 0
cd "$root" && uv run --group web pygbag --build "$here"
du -sh "$here/build/web" "$here/build/web/"*
