# HBC Version der VI-Suite 

Fork of VI-Suite by Ryan Southall ([https://github.com/rgsouthall](https://github.com/rgsouthall)).
With some Patches developed at HBC (Biberach University of Applied Sciences).
Currently testing and developing on Blender 5.X.

## Installation

via ready-built blender-extensions at (OS-specific downloads):

https://bwsyncandshare.kit.edu/s/w5ftGjwF2Qe4JdQ

Requirements:

- Blender 5.1 or newer
- Windows x64, Linux x64 (glibc 2.28 or newer) or macOS 14 (Sonoma) or newer on Apple Silicon.
  Intel Macs are not supported (Blender 5 runs on Apple Silicon only).

## Build-Guide

see [./build_guide.md](hbc_downstream/build_guide.md)

## TODO

### Energetische Simulation mit EnVi

- [x] Operative Raumtemperatur als Output ergänzen
- [x] Zusätzliche Outputs: rdd, edd und HTML

### Verteilung und Installation

- [x] VI-Suite als Extension mit Wheels builden ?
- [ ] ~~Windows Install Skript bearebiten und testen mit Download nach U:\, entpacken nach %USERPROFILE% ... damit dürfte alles dann bei wiederholter Nutzung sehr schnell gehen~~
- [x] macOS (Apple Silicon): EnergyPlus-Start, Quarantäne, Fortschrittsfenster (siehe `docs/macos_plan.md`)
- [x] macOS-CI: Build, Installation, Smoke-Test, EnVi-Test (`.github/workflows/macos.yml`)

### Tests und Build für alle Plattformen

- [ ] Linux-CI (`ubuntu-latest`): `libegl1` installieren, sonst scheitert der PySide6-Import und Blender entfernt alle Wheels
- [ ] Windows-CI (`windows-latest`): Smoke- und EnVi-Test anpassen (Pfade, `.exe`, kein `xattr`/`otool`)
- [ ] pyroomacoustics für Linux: Das Wheel wird lokal gebaut und liegt nicht auf PyPI. In der CI bauen
      (manylinux) oder als Release-Asset ablegen, damit ein Linux-Build ohne lokale Dateien möglich ist
- [ ] `get_wheels.py` ohne Conda (nur `pip download`), damit die CI die Wheel-Liste selbst erzeugen und
      mit dem Manifest abgleichen kann
- [ ] Kompletter Build mit `build_blender_extension.sh --split-platforms` in der CI, Zips für alle Plattformen
      als Artefakt bzw. als GitHub-Release bei einem Tag
- [ ] CI-Matrix mit weiteren Blender-Versionen (z. B. 5.2, manuell bereits auf dem Mac genutzt)
- [ ] Inneres Extension-Zip im Artefakt eindeutig benennen (z. B. `vi-suite_HBC_v003-macos-arm64.zip`),
      damit es nicht mit dem Artefakt-Zip verwechselt wird
- [ ] Tests für LiVi (Radiance-Simulation), FloVi (netgen-Vernetzung, OpenFOAM) und AuVi (pyroomacoustics);
      bisher prüft die CI dort nur, ob die Programme starten bzw. importierbar sind

### Upstream / Pflege

- [ ] Upstream (rgsouthall) auf den absoluten rpath in der macOS-EnergyPlus-Binary hinweisen
- [ ] Nach jedem Merge aus `master` mit neuer EnergyPlus-Version auf einem Mac
      `build_scripts/fix_energyplus_rpath_macos.sh` ausführen (die macOS-CI meldet es, falls vergessen)
- [ ] `vi_func.py` und `vi_operators.py` nutzen CRLF-Zeilenenden, die übrigen Dateien LF: einheitlich
      festlegen (z. B. per `.gitattributes`)
