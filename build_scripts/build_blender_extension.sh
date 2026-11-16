#!/usr/bin/env bash
# Build the VI-Suite HBC Blender extension (one zip per platform).
#
# Needs the wheels (get_wheels.py) and blender_manifest.toml.
# Blender is taken from $BLENDER, else from "blender" on the PATH.
#
#   BLENDER=/path/to/blender-5.3.0-linux-x64/blender bash build_scripts/build_blender_extension.sh
#   BLENDER=/Applications/Blender.app/Contents/MacOS/Blender bash build_scripts/build_blender_extension.sh
#
# Optional: OUT_DIR (default: <repo>/assets/blender_extensions/Blender-<blender version>)
#
# Note: --split-platforms only filters the wheels. Unlike the CI build
# (ci_prepare_platform.py), each zip still contains the EPFiles/RadFiles/OFFiles
# folders of all platforms.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
BLENDER="${BLENDER:-$(command -v blender || true)}"

if [ -z "$BLENDER" ] || [ ! -x "$BLENDER" ]; then
    echo "Blender not found. Set BLENDER=/path/to/blender" >&2
    exit 1
fi

# extension version from the manifest, e.g. version = "0.0.5" -> v0.0.5 (same as the release tag)
VERSION="v$(sed -n 's/^version *= *"\(.*\)"/\1/p' "$REPO/blender_manifest.toml")"
BLENDER_VERSION="$("$BLENDER" --version | sed -n 's/^Blender \([0-9.]*\).*/\1/p' | head -1)"
OUT_DIR="${OUT_DIR:-$REPO/assets/blender_extensions/Blender-$BLENDER_VERSION}"

mkdir -p "$OUT_DIR"
echo "Building vi-suite_HBC_$VERSION with Blender $BLENDER_VERSION into $OUT_DIR"

"$BLENDER" --command extension build \
  --source-dir "$REPO" \
  --output-filepath "$OUT_DIR/vi-suite_HBC_${VERSION}.zip" \
  --split-platforms
