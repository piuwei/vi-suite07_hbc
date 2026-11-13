
installierte Version patchen (bsp. Linux)

```sh
cd ~/repos/vi-suite07_hbc
cp -u *.py ~/.config/blender/5.0/scripts/addons/vi-suite07_26-01_hbc/
```

- ~~use `bash create_archives.sh` for archive creation~~
  - use build_scripts
- use vi-suite07_hbc.zip for full install of vi-suite
- use vi-suite07_hbc_tiny.zip for quick updates of only the .py files

Updates von Master Pullen

```sh
git checkout master
git pull
git checkout hbc_downstream
git merge master
```

dann Konflikte lösen...

## Extension bauen

```sh
BLENDER=/pfad/zu/blender bash build_scripts/build_blender_extension.sh
```

## macOS

- Voraussetzung: **macOS 14 (Sonoma) oder neuer auf Apple Silicon**. Das scipy-Wheel braucht macOS 14,
  PySide6 macOS 13. Blender 5 läuft nicht mehr auf Intel-Macs, deshalb gibt es keinen `macos-x64`-Build.
- Installation in Blender über *Edit → Preferences → Get Extensions → Install from Disk* mit dem Zip
  für `macos-arm64`. Das Zip nicht vorher im Finder entpacken.
- Quarantäne: Dateien aus einem Browser-Download, die im Finder entpackt wurden, tragen das Attribut
  `com.apple.quarantine`, und macOS blockiert dann EnergyPlus, Radiance und OpenFOAM. Das Add-on entfernt
  das Attribut beim Laden aus seinen eigenen Programmordnern. Von Hand geht es so (Pfad anpassen):
  ```sh
  xattr -dr com.apple.quarantine ~/Library/Application\ Support/Blender/5.1/extensions/user_default/vi_suite_HBC
  ```
- EnergyPlus: Die mitgelieferte Binary ist für macOS repariert (rpath). Nach einem Merge mit neuer
  EnergyPlus-Version aus `master` auf einem Mac `bash build_scripts/fix_energyplus_rpath_macos.sh` ausführen.
- Automatischer Test: `.github/workflows/macos.yml` baut und testet die Extension bei jedem Push
  (siehe `docs/macos_plan.md`).

## Dependencies für VI-Suite installieren

... OBSOLET
=> Einfach blender Extension nutzen...

aktueller Ablageordner: [bwsyncandshare](https://bwsyncandshare.kit.edu/f/4707870457)

### Ubuntu

in das übergerdnete Verzeichnis der Blender installation wechseln

```sh
cd ~/simulationssoftware/
```

Abhängigkeiten für pyroomacoustics in python3.11-dev (g++ compiler)

```sh
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11-dev
```

```sh
python3.11 -m pip install matplotlib kivy openimageio pyside6 scipy --target='~/.config/blender/4.4/scripts/modules'
python3.11 -m pip install pyroomacoustics --target='~/.config/blender/4.4/scripts/modules'
python3.11 -m pip install numpy==1.26.4 --target='~/.config/blender/4.4/scripts/modules'
```

für numpy.core.multiarray nötig: numpy==1.26.4

### Windows ohne Privilegien

```cmd
set BLENDER_VERSION=4.4
set BLENDER_FULL_VERSION=4.4.3
set BLENDER_ZIP_NAME=blender-%BLENDER_FULL_VERSION%-windows-x64.zip
set BLENDER_FOLDER_NAME=blender-%BLENDER_FULL_VERSION%-windows-x64

set TARGET_ROOT_PATH=%USERPROFILE%\Documents
set BLENDER_DOWNLOAD_URL=https://download.blender.org/release/Blender%BLENDER_VERSION%/%BLENDER_ZIP_NAME%
set BLENDER_INSTALL_PATH=%TARGET_ROOT_PATH%\%BLENDER_FOLDER_NAME%

set BLENDER_PYTHON_EXE=%BLENDER_INSTALL_PATH%\%BLENDER_VERSION%\python\bin\python.exe
%BLENDER_PYTHON_EXE% -m pip config --global set global.trusted-host "pypi.org files.pythonhosted.org"
%BLENDER_PYTHON_EXE% -m pip install --upgrade pip
%BLENDER_PYTHON_EXE% -m pip install matplotlib kivy openimageio pyside6 pyroomacoustics scipy --target=%MODULE_TARGET_PATH%
```

### OpenSuse

auf compute2 durchgeführt, 06/2025 mit neuer visuite Version (python3.13, nicht mehr 3.11):

```sh
zypper install python313-matplotlib python313-imageio python313-scipy python313-pyroomacoustics python313-pyside6
python3.13 -m pip install OpenImageIO --break-system-packages
```
