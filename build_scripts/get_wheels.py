#!/usr/bin/env python3

import os
import subprocess
import sys
from pathlib import Path
from typing import List

# select conda environment to get the wheels
CONDA_ENV = os.environ.get("CONDA_ENV", "visuite_313")
PYTHON_VERSION = "3.13"

REQUIREMENTS_FILE = "./requirements.txt"
SUBDIR = ""  # blank str "" if no subdir
MAIN_DEST_DIR = f"../wheels{SUBDIR}"
NGSOLVE_DEST_DIR = f"../ngsolve_wheels{SUBDIR}"
PYROOMACOUSTICS_DEST_DIR = f"../pyroomacoustics_wheels{SUBDIR}"
NG_SOLVE_PACKAGES: List[str] = ["mkl-service", "ngsolve"]
WINDOWS_PLATFORMS = ["win_amd64"]
LINUX_GLIBC_PLATFORMS = [
    "linux_x86_64",
    "manylinux_2_34_x86_64",
    "manylinux_2_28_x86_64",
    "manylinux_2_17_x86_64",
    "manylinux_1_17_x86_64",
    "manylinux2014_x86_64",
]

# LINUX_MUSL_PLATFORMS = [
#     "musllinux_1_2_x86_64",
#     ]

MACOS_X86_PLATFORMS = [
    "macosx_10_9_x86_64",
    "macosx_10_14_x86_64",
    "macosx_10_9_universal2",
    "macosx_10_12_x86_64",
    "macosx_11_0_universal2",
    "macosx_12_0_x86_64",
    "macosx_13_0_universal2",
    "macosx_14_0_x86_64",
]

MACOS_ARM64_PLATFORMS = [
    "macosx_10_9_universal2",
    "macosx_11_0_arm64",
    "macosx_11_0_universal2",
    "macosx_12_0_universal2",
    "macosx_13_0_universal2",
    "macosx_14_0_universal2",
    "macosx_14_0_arm64",
]


def build_download_command(
    env: str,
    dest_dir: str,
    sub_platforms: List[str],
    req_file: str = None,
    pkg_str: str = None,
):
    if req_file:
        cmd = [
            "conda",
            "run",
            "-n",
            env,
            sys.executable,
            "-m",
            "pip",
            "download",
            "-r",
            req_file,
            "--dest",
            dest_dir,
            "--only-binary=:all:",
            f"--python-version={PYTHON_VERSION}",
        ]
    elif pkg_str:
        cmd = [
            "conda",
            "run",
            "-n",
            env,
            sys.executable,
            "-m",
            "pip",
            "download",
            pkg_str,
            "--dest",
            dest_dir,
            "--only-binary=:all:",
            f"--python-version={PYTHON_VERSION}",
        ]

    for s_plat in sub_platforms:
        cmd.extend(["--platform", s_plat])

    print("--------------------")
    print(cmd)
    print("####################")
    return cmd


def run_pip_download_in_env(
    env: str,
    dest_dir: str,
    platforms: List[str],
    req_file: str = None,
    pkg_str: str = None,
) -> None:
    """Download wheels using pip from specific conda environment."""

    Path(dest_dir).mkdir(exist_ok=True)

    if req_file:
        cmd = build_download_command(
            env, dest_dir, sub_platforms=platforms, req_file=req_file
        )
    elif pkg_str:
        cmd = build_download_command(
            env, dest_dir, sub_platforms=platforms, pkg_str=pkg_str
        )
    else:
        print("PLEASE DEFINE pkg_str or req_file")

    subprocess.run(cmd, check=True)

    print(f"Downloaded wheels to {dest_dir}")


def main():

    all_platforms = [
        WINDOWS_PLATFORMS,
        LINUX_GLIBC_PLATFORMS,
        MACOS_ARM64_PLATFORMS,
        MACOS_X86_PLATFORMS,
    ]

    for sub_plats in all_platforms:
        # Download all the main packages
        run_pip_download_in_env(
            CONDA_ENV, MAIN_DEST_DIR, sub_plats, req_file=REQUIREMENTS_FILE
        )

    # Download NGSolve packages and dependencies for linux
    run_pip_download_in_env(
        CONDA_ENV,
        NGSOLVE_DEST_DIR,
        LINUX_GLIBC_PLATFORMS,
        pkg_str="mkl-service",
    )
    run_pip_download_in_env(
        CONDA_ENV, NGSOLVE_DEST_DIR, LINUX_GLIBC_PLATFORMS, pkg_str="ngsolve"
    )

    # NGSolve Windows
    run_pip_download_in_env(
        CONDA_ENV, NGSOLVE_DEST_DIR, WINDOWS_PLATFORMS, pkg_str="ngsolve"
    )

    # NGSolve MacOS Arm64
    run_pip_download_in_env(
        CONDA_ENV, NGSOLVE_DEST_DIR, MACOS_ARM64_PLATFORMS, pkg_str="ngsolve"
    )
    # NGSolve MacOS X86
    run_pip_download_in_env(
        CONDA_ENV, NGSOLVE_DEST_DIR, MACOS_X86_PLATFORMS, pkg_str="ngsolve"
    )

    # -- PYROOMACOUSTICS
    # Windows and MacOS Wheels for pyroomacoustics are available on PyPI
    run_pip_download_in_env(
        CONDA_ENV, MAIN_DEST_DIR, WINDOWS_PLATFORMS, pkg_str="pyroomacoustics"
    )
    # ARM64
    run_pip_download_in_env(
        CONDA_ENV,
        MAIN_DEST_DIR,
        MACOS_ARM64_PLATFORMS,
        pkg_str="pyroomacoustics",
    )
    # x86
    run_pip_download_in_env(
        CONDA_ENV,
        MAIN_DEST_DIR,
        MACOS_X86_PLATFORMS,
        pkg_str="pyroomacoustics",
    )

    # get pyroomacoustic from local files for Linux
    # requires active install of pyroomacoustics
    # (try `pip install pyroomacoustics` in your CONDA_ENV)
    pra_linux_cmd = [
        "conda",
        "run",
        "-n",
        CONDA_ENV,
        "pip",
        "wheel",
        "pyroomacoustics",
        "--wheel-dir",
        PYROOMACOUSTICS_DEST_DIR,
    ]
    subprocess.run(pra_linux_cmd, check=True)

    # -- OUTPUT
    sorted_wheels = sorted(
        list(Path(MAIN_DEST_DIR).glob("*.whl"))
        + list(Path(NGSOLVE_DEST_DIR).glob("*.whl"))
        + list(Path(PYROOMACOUSTICS_DEST_DIR).glob("*.whl")),
        key=lambda path: path.name,
    )

    wheel_count = len(sorted_wheels)
    print(f"Downloaded {wheel_count} wheels")

    # list wheels for copying to blender_manifest.toml
    prev_name = ""
    print("[")
    for full_path in sorted_wheels:
        name = full_path.name.split("-")[0]
        if prev_name != name:
            print(f"# -- {name}")
        print("\t" + '"' + "./" + str(full_path) + '"' + ",")
        prev_name = name
    print("]")


if __name__ == "__main__":
    main()
