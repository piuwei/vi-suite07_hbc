# vi-suite07

VI-Suite release for Blender 4.4 (experimental)

## hbc downstream branch

- use `bash create_archives.sh` for archive creation
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

### Dependencies für VI-Suite installieren

#### Ubuntu

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

## TODO

- [ ] VI-Suite als Extension mit Wheels builden ?
- [ ] Windows Install Skript bearebiten und testen mit Download nach U:\, entpacken nach %USERPROFILE% ... damit dürfte alles dann bei wiederholter Nutzung sehr schnell gehen
