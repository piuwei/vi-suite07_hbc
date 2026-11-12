# Plan: VI-Suite HBC auf macOS lauffähig machen

Stand: 12.11.2026 (Schritte 1–7 erledigt, offen: manueller Test auf einem Mac, PR nach `hbc_downstream`) · Branch: `hbc_downstream`

Zielplattform: **macOS arm64 (Apple Silicon)**. Blender ab 5.0 läuft nur noch auf Apple Silicon.

## Befund EnergyPlus (Blocker)

`EPFiles/darwin/energyplus-25.1.0` lädt `@rpath/libenergyplusapi.25.1.0.dylib`.
Der einzige eingetragene Suchpfad (`LC_RPATH`) zeigt auf einen Build-Ordner auf dem Rechner des Upstream-Autors:

```
/Users/rs6/Downloads/EnergyPlus-25.1.0-WithDSOASpaceListFixes/build-wheel/Products
```

Auf jedem anderen Mac findet dyld die Bibliothek deshalb nicht. Der Start bricht mit
„Library not loaded … no such file“ ab (Returncode −6), und es wird keine `.err` geschrieben.
Dateinamen und Symlinks sind korrekt. `ExpandObjects` ist nicht betroffen, es hängt nur von `libSystem` ab.

## Schritte

### 1. EnergyPlus-Start im Code absichern (Lösung A) – *erledigt, im Runner bestätigt*
- Auf macOS beim Start von EnergyPlus `DYLD_LIBRARY_PATH=<EPFiles/darwin>` nur an den Kindprozess übergeben.
  Die Binary bleibt unverändert, die Signatur bleibt gültig.
- Vor der Simulation `energyplus --version` testen und bei einem Fehler die Meldung im Blender-Report
  und im `vi-suite-log` anzeigen, statt still abzubrechen.

### 2. Binary reparieren (Lösung B) – *erledigt, im Runner bestätigt*
- Auf einem Mac oder im macOS-Runner ausführen:
  ```sh
  install_name_tool -add_rpath @executable_path EPFiles/darwin/energyplus-25.1.0
  codesign -f -s - EPFiles/darwin/energyplus-25.1.0
  ```
- Die reparierte Binary ist committet. Damit funktioniert auch `energyplus --version` im Terminal.
- Nach einem Merge mit neuer EnergyPlus-Version auf einem Mac `bash build_scripts/fix_energyplus_rpath_macos.sh`
  ausführen. Der Smoke-Test schlägt fehl, solange die Reparatur fehlt.
- Lösung A bleibt als Absicherung und für die Fehlermeldung vor der Simulation drin.
- Den Upstream-Autor auf den absoluten rpath hinweisen.

### 3. Manifest aufräumen (`blender_manifest.toml`) – *erledigt*
- `macos-x64` aus `platforms` entfernt, ebenso alle reinen `macosx_*_x86_64`-Wheels. Die `universal2`-Wheels bleiben.
- Doppelte Einträge entfernt (numpy und scipy aus mehreren Wheel-Ordnern).
- `cython` und `pybind11` entfernt. pyroomacoustics führt sie zwar als Abhängigkeit auf, importiert sie aber nicht.
  Blender prüft beim Installieren keine Abhängigkeiten.
- `numpy` entfernt, Blender 5.1 bringt numpy 2.3.4 mit. Das passt zu scipy (≥ 1.26.4), matplotlib,
  contourpy und netgen.
- Ergebnis: 65 statt 89 Wheels, die Liste für macOS arm64 hat 21 statt 23.
- `get_wheels.py` lädt keine macOS-x86-Wheels mehr und lässt numpy, Cython, pybind11 und Dubletten
  in der ausgegebenen Liste weg.

### 4. macOS-Runner (GitHub Actions) – *erledigt (12.11.2026: alle Tests grün, inkl. Lösung B, Manifest, Quarantäne, Laupheim)*
Workflow `.github/workflows/macos.yml` auf `macos-latest` (arm64):
1. Blender 5.1 (arm64) herunterladen und mounten.
2. Mit `build_scripts/ci_prepare_platform.py --platform macos-arm64` das Manifest auf macOS arm64
   filtern und genau die eingetragenen Wheels von PyPI laden. Dabei wird geprüft, ob alle Einträge existieren.
3. Mit `blender --command extension build --split-platforms` bauen.
4. Mit `blender --command extension install-file` installieren.
5. `tests/smoke_test.py`: Add-on aktivieren, Importe testen (matplotlib, scipy, PySide6, netgen/ngsolve,
   pyroomacoustics …), `energyplus --version` mit und ohne Lösung A, Mini-Simulation (`tests/data/mini.idf`),
   ExpandObjects und `rtrace -version`.
6. `tests/envi_blend_test.py` mit `tests/data/simple_cube.blend`: EnVi-Geometrie- und IDF-Export über die
   Node-Operatoren, danach EnergyPlus mit derselben Kommandozeile wie `node.ensim`.
   Prüfung: `.err`/`.eso` geschrieben, 0 Severe Errors.
   Die Wetterdatei aus dem .blend (Laupheim TMYx, climate.onebuilding.org) liegt als Kopie in `tests/data/`.
7. Berichte und Logs als Artefakt hochladen, eine Übersicht erscheint in der Job-Zusammenfassung.
   Das Zip wird nur bei manuellem Start mit `upload_zip` hochgeladen.

Zusätzlich lokal unter Linux mit Blender 5.1.2 getestet: Build, Installation, Smoke-Test und EnVi-Test laufen
durch. Ausnahme: pyroomacoustics, weil das Linux-Wheel lokal gebaut wird.

Voraussetzungen: Schreibzugriff der Claude GitHub App mit der Berechtigung `workflows`.
Für private Repos zählen macOS-Minuten zehnfach.

### 5. macOS-Voraussetzungen dokumentieren – *erledigt (README, build_guide.md)*
- Das scipy-Wheel braucht macOS ≥ 14, PySide6 ≥ 13, also gilt: **mindestens macOS 14 auf Apple Silicon**.
- Die `universal2`-Wheels installiert Blender korrekt (im Runner geprüft).
- **Offen:** Die Qt-Fenster (Fortschrittsbalken) und den modalen Simulations-Knopf auf einem echten Mac
  prüfen. Das geht im Runner nicht.

### 6. Quarantäne – *erledigt*
- Beim Laden entfernt das Add-on auf macOS `com.apple.quarantine` aus `EPFiles/darwin`, `RadFiles/darwin`
  und `OFFiles/darwin`, aber nur dann, wenn das Attribut gesetzt ist.
- Der Runner setzt das Attribut nach der Installation absichtlich, und der Smoke-Test prüft, dass es
  bei `energyplus` und `rtrace` wieder entfernt ist.
- Der Befehl für die Entfernung von Hand steht in `build_guide.md`.

### 7. Build-Skript portabel machen – *erledigt*
- `build_blender_extension.sh` nimmt Blender aus `$BLENDER` (oder `blender` im PATH), funktioniert aus
  jedem Verzeichnis und liest die Versionsnummer aus dem Manifest.

## Gefundene Fehler
- `__init__.py`: Der netgen-Workaround suchte die Wheels in `/ngsolve_wheels` (Wurzelverzeichnis)
  statt im Extension-Ordner. Ist korrigiert. Ohne die Korrektur ist `netgen`/`ngsolve` nicht importierbar,
  weil das Wheel seine Pakete unter `.data/data/lib/...` ablegt und Blender diese nicht einrichtet.
- Linux: Ohne `libEGL` scheitert der PySide6-Import beim Aktivieren, und Blender entfernt danach alle Wheels.
  Auf Rechnern ohne Desktop (Server) muss `libegl1` installiert sein.

## Erledigt
- Upstream-Merge: `hbc_downstream` enthält alle Commits von `master`.
- Große Dateien: Die Wheels stehen in `.gitignore` und landen nicht im Repo.
