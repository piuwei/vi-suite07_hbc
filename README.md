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
pip install matplotlib kivy openimageio pyside6 scipy --target='/home/pius/.config/blender/4.4/scripts/modules'
pip install pyroomacoustics --target='/home/pius/.config/blender/4.4/scripts/modules'
pip install numpy==1.26.4 --target='/home/pius/.config/blender/4.4/scripts/modules'
```

für numpy.core.multiarray nötig: numpy==1.26.4

## TODO

- [ ] VI-Suite als Extension mit Wheels builden ?
- [ ] Windows Install Skript bearebiten und testen mit Download nach U:\, entpacken nach %USERPROFILE% ... damit dürfte alles dann bei wiederholter Nutzung sehr schnell gehen
