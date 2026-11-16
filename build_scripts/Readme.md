# Build scripts for VI-Suite HBC

Releases are built by GitHub Actions (`.github/workflows/release.yml`, started by a version tag).
The scripts here are used by the CI and for local builds.

## Wheels
- `requirements.txt`: Python packages the add-on needs (wheels are fetched for these)
- `get_wheels.py`
  - downloads the wheels for all platforms with `pip download` (no conda; any Python >= 3.11,
    works from any directory) and prints the wheel list for `blender_manifest.toml`
  - `--check`: compare with the manifest, `--write`: replace the wheel list in the manifest
  - `--clean`: empty the download folders first, so no old versions end up in the list
  - fails if a Windows wheel contains a path that would exceed MAX_PATH (260) in the Blender
    extension folder

## Build
- `ci_prepare_platform.py` (CI): prepares a single-platform build: filters and downloads the wheels
  from the manifest and excludes the program folders of the other platforms
  (`EPFiles/`, `RadFiles/`, `OFFiles/`, `Python/`)
- `build_blender_extension.sh` (local): builds one zip per platform with `--split-platforms`;
  needs the wheels and `blender_manifest.toml`. Blender is taken from `$BLENDER` (or `blender` on
  the PATH), works from any directory:
  `BLENDER=/path/to/blender bash build_scripts/build_blender_extension.sh`.
  These zips still contain the program folders of all platforms.

## Maintenance
- `fix_energyplus_rpath_macos.sh`: run on a Mac after a new EnergyPlus binary was merged from master
- `check_line_endings.py`: fails if a change converts the line endings of a whole file
  (used by `.github/workflows/checks.yml`)
