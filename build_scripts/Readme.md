# Scripts for building Vi-Suite HBC-Version

- get_wheels.py
  - Get required Wheels (run inside `build_scripts`, needs the conda env `CONDA_ENV`)
  - prints the wheel list for `blender_manifest.toml`
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
