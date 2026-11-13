#!/usr/bin/env python3
"""Download the Python wheels for the VI-Suite HBC extension (no conda needed).

Uses `pip download` with --platform/--python-version, so it can run with any
Python >= 3.11 on any OS. Only the Linux pyroomacoustics wheel has to be built
locally (there is none on PyPI); that needs a Python 3.13 interpreter.

Usage (from anywhere):
    python3 build_scripts/get_wheels.py            # download, print wheel list
    python3 build_scripts/get_wheels.py --check    # also compare with blender_manifest.toml
    python3 build_scripts/get_wheels.py --write    # also replace the wheel list in the manifest

Options:
    --python313 PATH   Python 3.13 used to build the Linux pyroomacoustics wheel
                       (default: this interpreter if it is 3.13, else `python3.13` on PATH;
                       skipped with a warning if none is found)

Wheels land in wheels/, ngsolve_wheels/ and pyroomacoustics_wheels/ in the
repository root (all git-ignored), with the same paths as in the manifest.
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
PYROOMACOUSTICS_DIR = "pyroomacoustics_wheels"

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


def find_python313(explicit):
    if explicit:
        return explicit
    if sys.version_info[:2] == (3, 13):
        return sys.executable
    return shutil.which("python3.13")


def build_pyroomacoustics_linux(python313):
    """pyroomacoustics has no Linux wheel on PyPI: build it (cp313, linux_x86_64)."""
    if not sys.platform.startswith("linux"):
        print("WARNING: the Linux pyroomacoustics wheel can only be built on Linux, skipped "
              "(the Linux CI builds it).")
        return
    if not python313:
        print("WARNING: no Python 3.13 found, Linux pyroomacoustics wheel skipped "
              "(use --python313 PATH; the Linux CI builds it anyway).")
        return
    dest = ROOT / PYROOMACOUSTICS_DIR
    dest.mkdir(exist_ok=True)
    cmd = [python313, "-m", "pip", "wheel", "--no-deps", "--wheel-dir", str(dest), "pyroomacoustics"]
    print("$ " + " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def wheel_list():
    """Manifest paths of all downloaded wheels, without excluded packages and duplicates."""
    found = sorted(
        (p for d in (MAIN_DIR, NGSOLVE_DIR, PYROOMACOUSTICS_DIR) for p in (ROOT / d).glob("*.whl")),
        key=lambda p: (p.name.lower(), p.parent.name),
    )
    out, seen = [], set()
    for p in found:
        if p.name.split("-")[0].lower() in EXCLUDE_FROM_MANIFEST or p.name in seen:
            continue
        seen.add(p.name)
        out.append(f"./{p.parent.name}/{p.name}")
    return out


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
    ap.add_argument("--python313", help="Python 3.13 for building the Linux pyroomacoustics wheel")
    args = ap.parse_args()

    for platforms in (WINDOWS_PLATFORMS, LINUX_GLIBC_PLATFORMS, MACOS_ARM64_PLATFORMS):
        pip_download(MAIN_DIR, platforms, requirements=REQUIREMENTS_FILE)

    pip_download(NGSOLVE_DIR, LINUX_GLIBC_PLATFORMS, package="mkl-service")
    for platforms in (LINUX_GLIBC_PLATFORMS, WINDOWS_PLATFORMS, MACOS_ARM64_PLATFORMS):
        pip_download(NGSOLVE_DIR, platforms, package="ngsolve")

    # pyroomacoustics: wheels on PyPI for Windows and macOS, built locally for Linux
    for platforms in (WINDOWS_PLATFORMS, MACOS_ARM64_PLATFORMS):
        pip_download(MAIN_DIR, platforms, package="pyroomacoustics")
    build_pyroomacoustics_linux(find_python313(args.python313))

    wheels = wheel_list()
    block = wheel_block(wheels)
    print(f"\n{len(wheels)} wheels for blender_manifest.toml:\n")
    print(block)

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
