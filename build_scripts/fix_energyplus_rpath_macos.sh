#!/usr/bin/env bash
# Make the bundled macOS EnergyPlus binary find libenergyplusapi next to it.
#
# The upstream binary only has an absolute LC_RPATH pointing to the build
# directory on the upstream author's machine, so on every other Mac it aborts
# with "Library not loaded: @rpath/libenergyplusapi.*.dylib".
# This adds @executable_path as rpath and re-signs the binary (ad-hoc).
#
# Run on a Mac (needs Xcode command line tools), e.g. after merging a new
# EnergyPlus version from master:
#   bash build_scripts/fix_energyplus_rpath_macos.sh [EPFiles/darwin]
set -euo pipefail

dir="${1:-$(dirname "$0")/../EPFiles/darwin}"
exe="$(cd "$dir" && ls energyplus-[0-9]* | head -1)"
cd "$dir"

if otool -l "$exe" | grep -A2 LC_RPATH | grep -q "path @executable_path "; then
    echo "$exe already has @executable_path rpath"
else
    install_name_tool -add_rpath @executable_path "$exe"
    codesign --force --sign - "$exe"
    echo "added @executable_path rpath to $exe and re-signed"
fi

./"$exe" --version
