#!/usr/bin/env python3
"""Download the Python wheels for the VI-Suite HBC extension (no conda needed).

Uses `pip download` with --platform/--python-version, so it can run with any
Python >= 3.11 on any OS. All wheels come from PyPI (pyroomacoustics has a
manylinux wheel since 0.10.1).

Usage (from anywhere):
    python3 build_scripts/get_wheels.py            # download, print wheel list
    python3 build_scripts/get_wheels.py --check    # also compare with blender_manifest.toml
    python3 build_scripts/get_wheels.py --write    # also replace the wheel list in the manifest
    add --clean to empty the download folders first (so no old versions are listed)

Wheels land in wheels/ and ngsolve_wheels/ in the repository root (both
git-ignored), with the same paths as in the manifest.
"""

import argparse
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

PYTHON_VERSION = "3.13"
ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "blender_manifest.toml"
REQUIREMENTS_FILE = Path(__file__).resolve().parent / "requirements.txt"

MAIN_DIR = "wheels"
NGSOLVE_DIR = "ngsolve_wheels"

WINDOWS_PLATFORMS = ["win_amd64"]
LINUX_GLIBC_PLATFORMS = [
    "linux_x86_64",
    "manylinux_2_34_x86_64",
    "manylinux_2_28_x86_64",
    "manylinux_2_17_x86_64",
    "manylinux_1_17_x86_64",
    "manylinux2014_x86_64",
]
# Blender >= 5.0 is Apple Silicon only, no macOS x86_64 wheels needed
MACOS_ARM64_PLATFORMS = [
    "macosx_10_9_universal2",
    "macosx_11_0_arm64",
    "macosx_11_0_universal2",
    "macosx_12_0_universal2",
    "macosx_13_0_universal2",
    "macosx_14_0_universal2",
    "macosx_14_0_arm64",
]

# Windows: Blender unpacks the wheels into
#   C:\Users\<user>\AppData\Roaming\Blender Foundation\Blender\<x.y>\extensions\.local\lib\python3.13\site-packages\
# which is about 110 characters plus the user name. Paths longer than MAX_PATH (260) fail
# to unpack, so file paths inside Windows wheels must stay below this limit, with room
# for longer user names.
WINDOWS_SITE_PACKAGES = (r"C:\Users\{user}\AppData\Roaming\Blender Foundation\Blender\5.3"
                         r"\extensions\.local\lib\python3.13\site-packages" + "\\")
WINDOWS_MAX_PATH = 260
WINDOWS_USER_RESERVE = 20  # characters reserved for the user name

# Not listed in the manifest:
# - numpy: Blender ships its own numpy
# - cython, pybind11: build-time only (declared but not imported by pyroomacoustics)
EXCLUDE_FROM_MANIFEST = {"numpy", "cython", "pybind11"}


def pip_download(dest_dir, platforms, requirements=None, package=None):
    dest = ROOT / dest_dir
    dest.mkdir(exist_ok=True)
    cmd = [sys.executable, "-m", "pip", "download", "--dest", str(dest),
           "--only-binary=:all:", f"--python-version={PYTHON_VERSION}"]
    cmd += ["-r", str(requirements)] if requirements else [package]
    for p in platforms:
        cmd += ["--platform", p]
    print("$ " + " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def wheel_list():
    """Manifest paths of all downloaded wheels, without excluded packages and duplicates."""
    found = sorted(
        (p for d in (MAIN_DIR, NGSOLVE_DIR) for p in (ROOT / d).glob("*.whl")),
        key=lambda p: (p.name.lower(), p.parent.name),
    )
    out, seen = [], set()
    for p in found:
        if p.name.split("-")[0].lower() in EXCLUDE_FROM_MANIFEST or p.name in seen:
            continue
        seen.add(p.name)
        out.append(f"./{p.parent.name}/{p.name}")
    return out


def check_windows_paths(wheels):
    """Return (wheel, longest path inside, total length) for Windows wheels that would
    exceed MAX_PATH when unpacked into the Blender extension folder."""
    import zipfile
    prefix = len(WINDOWS_SITE_PACKAGES.format(user="x" * WINDOWS_USER_RESERVE))
    too_long = []
    for w in wheels:
        if "win_amd64" not in w:
            continue
        names = zipfile.ZipFile(ROOT / w).namelist()
        longest = max(names, key=len)
        if prefix + len(longest) >= WINDOWS_MAX_PATH:
            too_long.append((w, longest, prefix + len(longest)))
    return too_long


def wheel_block(wheels):
    lines, prev = ["wheels = ["], None
    for w in wheels:
        name = w.rsplit("/", 1)[1].split("-")[0].lower()
        if name != prev:
            lines.append(f"  # -- {name}")
            prev = name
        lines.append(f'  "{w}",')
    lines.append("]")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="compare with the wheel list in the manifest")
    ap.add_argument("--write", action="store_true", help="replace the wheel list in the manifest")
    ap.add_argument("--clean", action="store_true", help="empty the download folders first")
    args = ap.parse_args()

    if args.clean:
        for d in (MAIN_DIR, NGSOLVE_DIR):
            shutil.rmtree(ROOT / d, ignore_errors=True)

    for platforms in (WINDOWS_PLATFORMS, LINUX_GLIBC_PLATFORMS, MACOS_ARM64_PLATFORMS):
        pip_download(MAIN_DIR, platforms, requirements=REQUIREMENTS_FILE)

    pip_download(NGSOLVE_DIR, LINUX_GLIBC_PLATFORMS, package="mkl-service")
    for platforms in (LINUX_GLIBC_PLATFORMS, WINDOWS_PLATFORMS, MACOS_ARM64_PLATFORMS):
        pip_download(NGSOLVE_DIR, platforms, package="ngsolve")

    wheels = wheel_list()
    block = wheel_block(wheels)
    print(f"\n{len(wheels)} wheels for blender_manifest.toml:\n")
    print(block)

    too_long = check_windows_paths(wheels)
    for w, path, n in too_long:
        print(f"\nERROR: {w}: '{path}' would be {n} characters long on Windows "
              f"(limit {WINDOWS_MAX_PATH}, user name up to {WINDOWS_USER_RESERVE} characters). "
              f"Pin an older version in requirements.txt.")
    if too_long and (args.check or args.write):
        return 1

    text = MANIFEST.read_text()
    current = tomllib.loads(text).get("wheels", [])

    rc = 0
    if args.check:
        added = sorted(set(wheels) - set(current))
        removed = sorted(set(current) - set(wheels))
        print(f"\nManifest check: {len(current)} wheels in the manifest, {len(wheels)} downloaded")
        for w in added:
            print(f"  + {w}")
        for w in removed:
            print(f"  - {w}")
        if added or removed:
            print("Manifest differs from the downloaded wheels (run with --write to update it).")
            rc = 1
        else:
            print("Manifest is up to date.")

    if args.write:
        new_text, n = re.subn(r"^wheels\s*=\s*\[.*?^\]", block, text, count=1, flags=re.S | re.M)
        if n != 1:
            sys.exit("Could not find the wheels = [...] block in the manifest")
        tomllib.loads(new_text)
        MANIFEST.write_text(new_text)
        print(f"\nUpdated {MANIFEST.relative_to(ROOT)}")
        rc = 0

    return rc


if __name__ == "__main__":
    sys.exit(main())
