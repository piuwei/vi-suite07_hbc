# Entwicklung der VI-Suite HBC

Hinweise für die Entwicklung, das Testen und das Veröffentlichen der Extension.
Für Nutzer siehe [README.md](../README.md).

## Überblick

- **Build und Release:** siehe [build_guide.md](build_guide.md) (Extension bauen, Wheels, Release per Tag)
- **Skripte:** siehe [build_scripts/Readme.md](../build_scripts/Readme.md)
- **macOS-Besonderheiten** (EnergyPlus-rpath, Quarantäne): siehe [macos_plan.md](macos_plan.md)

## Tests (GitHub Actions)

| Workflow | Wann | Was |
|---|---|---|
| `macos.yml`, `linux.yml`, `windows.yml` | Pull Requests und Pushes auf `hbc_downstream` (nicht bei reinen Doku-Änderungen), manuell | Extension bauen, installieren, `tests/smoke_test.py` und `tests/envi_blend_test.py` mit der neuesten Blender-Version. Linux: Build auf Ubuntu 24.04, Test desselben Zips auf 24.04 und 26.04 |
| `blender-versions.yml` | manuell | dieselben Tests für eine Liste von Blender-Versionen |
| `checks.yml` | Pull Requests | Zeilenenden (siehe unten) |
| `release.yml` | Tag `v<version>`, manuell | alle Plattformen bauen und testen, GitHub-Release anlegen |

## Unterstützte Blender-Versionen (Regel)

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

## Zeilenenden

Die Dateien behalten die Zeilenenden, die sie haben:

- Die meisten `.py`-Dateien des Add-ons stammen von Upstream (`master`) und nutzen CRLF, einige
  Upstream-Dateien sind gemischt. Neue Dateien dieses Forks (CI, Tests, Skripte, Doku) nutzen LF.
- Eine Datei komplett umzuwandeln (z. B. CRLF → LF durch den Editor) ist nicht erlaubt: Jede Zeile
  würde als geändert gelten, und Merges aus `master` gäben große Konflikte.
- Die Prüfung `build_scripts/check_line_endings.py` läuft bei jedem Pull Request
  (`.github/workflows/checks.yml`) und schlägt fehl, wenn ein PR die Zeilenenden einer ganzen Datei umstellt.
  Lokal: `python3 build_scripts/check_line_endings.py origin/hbc_downstream`

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
- [x] `get_wheels.py` ohne Conda (nur `pip download`), mit `--check` (Abgleich mit dem Manifest) und
      `--write` (Wheel-Liste im Manifest ersetzen)
- [x] Wheels aktualisiert (u. a. scipy 1.18, matplotlib 3.11, ngsolve 6.2.2608, pyroomacoustics 0.10.1 mit
      manylinux-Wheel von PyPI, kein eigener Build mehr); statt `PySide6` nur `PySide6-Essentials` 6.11.0
      (QtCore/QtGui/QtWidgets), dadurch kleinere Zips. PySide6 ab 6.11.1 enthält einen Pfad, der unter Windows
      im Blender-Extension-Ordner die 260-Zeichen-Grenze überschreitet; `get_wheels.py` prüft das jetzt
- [ ] PySide6-Essentials wieder aktualisieren, sobald eine Version ohne den zu langen Windows-Pfad erscheint
- [x] Build für alle Plattformen in der CI, GitHub-Release bei einem Tag `v<version>`
      (`.github/workflows/release.yml`, siehe [build_guide.md](build_guide.md))
- [x] Tests mit mehreren Blender-Versionen (5.1.2, 5.2.4, 5.3.0), siehe „Unterstützte Blender-Versionen“
- [x] Extension-Zip und CI-Artefakt eindeutig benennen (`vi-suite_HBC-<plattform>.zip` im Artefakt
      `vi-suite_HBC-<plattform>-extension`)
- [x] Radiance-Testrechnung im Smoke-Test (oconv + rtrace, Ergebnis wird mit dem exakten Wert verglichen)
- [ ] LiVi-Test über die Nodes (wie der EnVi-Test), braucht eine `.blend`-Datei mit LiVi-Nodes

### Upstream / Pflege

- [ ] Nach jedem Merge aus `master` mit neuer EnergyPlus-Version auf einem Mac
      `build_scripts/fix_energyplus_rpath_macos.sh` ausführen (die macOS-CI meldet es, falls vergessen)
- [x] Zeilenenden: Regel festgelegt (siehe „Zeilenenden“), CI-Prüfung `.github/workflows/checks.yml`
