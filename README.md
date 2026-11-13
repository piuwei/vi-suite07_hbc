# HBC Version der VI-Suite 

Fork of VI-Suite by Ryan Southall ([https://github.com/rgsouthall](https://github.com/rgsouthall)).
With some Patches developed at HBC (Biberach University of Applied Sciences).
Currently testing and developing on Blender 5.X.

## Installation

Download the ready-built Blender extension for your platform (one zip per platform) from the
GitHub releases of this repository:

https://github.com/piuwei/vi-suite07_hbc/releases

In Blender: *Edit → Preferences → Get Extensions → Install from Disk* and select the zip
(do not unpack it first).

**macOS / Safari:** Safari unpacks downloaded zip files automatically, and Blender cannot install the
resulting folder. Before downloading, switch off *Safari → Settings → General → "Open 'safe' files
after downloading"*, or download with another browser. If it was already unpacked, delete the folder
and download the zip again.

Requirements:

- Blender 5.1 or newer (tested with 5.1.2, 5.2.4 LTS and 5.3.0)
- Windows x64, Linux x64 (glibc 2.39 or newer, e.g. Ubuntu 24.04 or 26.04) or macOS 14 (Sonoma) or newer on Apple Silicon.
  Intel Macs are not supported (Blender 5 runs on Apple Silicon only).

## Unterstützte Blender-Versionen

- **Mindestversion bleibt Blender 5.1** (`blender_version_min = "5.1.0"` in `blender_manifest.toml`).
  Sie wird erst angehoben, wenn das Add-on mit 5.1 tatsächlich Probleme macht.
- **Getestet wird jede Version**, von der Mindestversion bis zur neuesten:
  - Pull Requests und Pushes auf `hbc_downstream` testen nur die **neueste Blender-Version**
    (derzeit 5.3.0, Standard in `.github/workflows/macos.yml`, `linux.yml`, `windows.yml` und `release.yml`).
  - Alle Versionen nach Bedarf, z. B. vor einem Release oder wenn eine neue Blender-Version erscheint:
    *Actions → Blender versions → Run workflow* (`.github/workflows/blender-versions.yml`).
    Die Versionsliste lässt sich beim Start anpassen und sollte immer die Mindestversion enthalten.
- Neue Blender-Version: Sie in die Standardliste von `blender-versions.yml` aufnehmen und, sobald
  sie dort grün ist, als neue Standardversion in den vier Workflows eintragen.

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

- [x] Linux-CI (`.github/workflows/linux.yml`, inkl. `libegl1`, ohne das der PySide6-Import scheitert und Blender alle Wheels entfernt)
- [x] Windows-CI (`.github/workflows/windows.yml`): Smoke- und EnVi-Test laufen unverändert
- [x] pyroomacoustics für Linux: Die Linux-CI baut das Wheel selbst (es liegt nicht auf PyPI)
- [x] `get_wheels.py` ohne Conda (nur `pip download`), mit `--check` (Abgleich mit dem Manifest) und
      `--write` (Wheel-Liste im Manifest ersetzen)
- [ ] Wheels aktualisieren: PyPI hat neuere Versionen (u. a. PySide6 6.12, das zusätzlich die großen Pakete
      `pyside6_webengine`/`pyside6_pdf` mitbringt) und inzwischen ein manylinux-Wheel für pyroomacoustics 0.10.1
      (dann läuft das Linux-Zip ab glibc 2.28, der CI-Build des Wheels entfällt)
- [x] Build für alle Plattformen in der CI, GitHub-Release bei einem Tag `v<version>`
      (`.github/workflows/release.yml`, siehe `build_guide.md`)
- [x] Tests mit mehreren Blender-Versionen (5.1.2, 5.2.4, 5.3.0), siehe „Unterstützte Blender-Versionen“
- [x] Extension-Zip und CI-Artefakt eindeutig benennen (`vi-suite_HBC-<plattform>.zip` im Artefakt
      `vi-suite_HBC-<plattform>-extension`)
- [x] Radiance-Testrechnung im Smoke-Test (oconv + rtrace, Ergebnis wird mit dem exakten Wert verglichen)
- [ ] LiVi-Test über die Nodes (wie der EnVi-Test), braucht eine `.blend`-Datei mit LiVi-Nodes

### Upstream / Pflege

- [ ] Nach jedem Merge aus `master` mit neuer EnergyPlus-Version auf einem Mac
      `build_scripts/fix_energyplus_rpath_macos.sh` ausführen (die macOS-CI meldet es, falls vergessen)
- [ ] `vi_func.py` und `vi_operators.py` nutzen CRLF-Zeilenenden, die übrigen Dateien LF: einheitlich
      festlegen (z. B. per `.gitattributes`)
