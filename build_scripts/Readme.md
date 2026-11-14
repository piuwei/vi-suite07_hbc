# Scripts for building Vi-Suite HBC-Version

- get_wheels.py
  - Downloads the required wheels for all platforms with `pip download` (no conda; any Python >= 3.11,
    works from any directory) and prints the wheel list for `blender_manifest.toml`
  - `--check`: compare with the manifest, `--write`: replace the wheel list in the manifest
  - `--clean`: empty the download folders first, so no old versions end up in the list
  - fails if a Windows wheel contains a path that would exceed MAX_PATH (260) in the Blender
    extension folder
- requirements.txt
  - Python Modules to get wheels for
- build_blender_extension.sh
  - build with blender for use as Blender-Extension, needs wheels and
    blender_manifest.toml configured
  - Blender is taken from `$BLENDER` (or `blender` on the PATH), works from any directory:
    `BLENDER=/path/to/blender bash build_scripts/build_blender_extension.sh`
- fix_energyplus_rpath_macos.sh
  - run on a Mac after a new EnergyPlus binary was merged from master
- ci_prepare_platform.py
  - used by the CI runner: single-platform build with the wheels from the manifest
- check_line_endings.py
  - fails if a change converts the line endings of a whole file (used by `.github/workflows/checks.yml`)
