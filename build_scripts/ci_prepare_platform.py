#!/usr/bin/env python3
"""Prepare a single-platform extension build (used by the CI runners).

- Reads the wheel list from blender_manifest.toml
- Keeps only the wheels that can be installed on the chosen platform / Python 3.13
- Downloads exactly these files from PyPI into the folders named in the manifest
- Rewrites the manifest to platforms = ["<platform>"] and the filtered wheel list

Because the files are fetched by their exact names, the run also checks that every
wheel listed in the manifest really exists on PyPI.

Usage (from the repository root):
    python3 build_scripts/ci_prepare_platform.py --platform macos-arm64
    python3 build_scripts/ci_prepare_platform.py --platform linux-x64 --skip-missing
    python3 build_scripts/ci_prepare_platform.py --platform windows-x64
"""

import argparse
import json
import re
import sys
import tomllib
import urllib.request
from pathlib import Path

PLATFORMS = ("macos-arm64", "linux-x64", "windows-x64")


def wheel_tags(filename):
    """Return (name, version, python tag, abi tag, platform tags) of a wheel file name."""
    parts = filename[:-4].split("-")
    name, version = parts[0], parts[1]
    py, abi, plat = parts[-3], parts[-2], parts[-1]
    return name, version, py, abi, plat.split(".")


def matches_platform(filename, platform):
    _name, _version, py, abi, plats = wheel_tags(filename)

    if not any(p in py.split(".") for p in ("cp313", "py3", "py2")) and abi != "abi3":
        return False

    for p in plats:
        if p == "any":
            return True
        if platform == "macos-arm64" and p.startswith("macosx_") and p.endswith(("_arm64", "_universal2")):
            return True
        if platform == "linux-x64" and p.startswith(("manylinux", "linux_")) and p.endswith("_x86_64"):
            return True
        if platform == "windows-x64" and p == "win_amd64":
            return True

    return False


def pypi_url(filename):
    name, version, *_ = wheel_tags(filename)
    with urllib.request.urlopen(f"https://pypi.org/pypi/{name}/{version}/json", timeout=60) as r:
        data = json.load(r)

    for f in data["urls"]:
        if f["filename"] == filename:
            return f["url"]

    raise FileNotFoundError(f"{filename} not found on PyPI ({name} {version})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--platform", choices=PLATFORMS, default="macos-arm64")
    ap.add_argument("--manifest", default="blender_manifest.toml")
    ap.add_argument("--skip-missing", action="store_true",
                    help="drop wheels that are not on PyPI (e.g. locally built ones) instead of failing")
    ap.add_argument("--no-download", action="store_true", help="only filter and rewrite the manifest")
    args = ap.parse_args()

    manifest = Path(args.manifest)
    root = manifest.parent
    text = manifest.read_text()
    wheels = tomllib.loads(text).get("wheels", [])

    keep, seen_files, dropped_dupes = [], set(), []

    for w in wheels:
        fn = Path(w).name
        if not matches_platform(fn, args.platform):
            continue
        if fn in seen_files:
            dropped_dupes.append(w)
            continue
        seen_files.add(fn)
        keep.append(w)

    names_all = {wheel_tags(Path(w).name)[0].lower() for w in wheels}
    names_mac = {wheel_tags(Path(w).name)[0].lower() for w in keep}

    print(f"Manifest lists {len(wheels)} wheels, {len(keep)} for {args.platform}")
    if dropped_dupes:
        print("Duplicate wheel files (listed in more than one folder), using first entry only:")
        for d in dropped_dupes:
            print(f"   {d}")
    if names_all - names_mac:
        print(f"Packages without a {args.platform} wheel (check whether they are needed there):")
        print("   " + ", ".join(sorted(names_all - names_mac)))

    errors, missing = [], []
    if not args.no_download:
        for w in keep:
            dest = root / w
            if dest.exists():
                print(f"   exists   {w}")
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                urllib.request.urlretrieve(pypi_url(dest.name), dest)
                print(f"   download {w}")
            except Exception as e:
                (missing if args.skip_missing else errors).append(w)
                print(f"   MISSING  {w}: {e}")

    keep = [w for w in keep if w not in missing]

    wheel_block = "wheels = [\n" + "".join(f'  "{w}",\n' for w in keep) + "]"
    text, n = re.subn(r"^wheels\s*=\s*\[.*?^\]", wheel_block, text, count=1, flags=re.S | re.M)
    if n != 1:
        sys.exit("Could not find the wheels = [...] block in the manifest")
    text, n = re.subn(r"^platforms\s*=\s*\[[^\]]*\]", f'platforms = ["{args.platform}"]', text, count=1, flags=re.M)
    if n != 1:
        sys.exit("Could not find platforms = [...] in the manifest")

    tomllib.loads(text)
    manifest.write_text(text)
    print(f"Rewrote {manifest} for {args.platform}")

    if errors:
        sys.exit(f"{len(errors)} wheel(s) listed in the manifest could not be downloaded")


if __name__ == "__main__":
    main()
