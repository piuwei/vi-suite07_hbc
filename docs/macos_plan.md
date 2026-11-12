# Plan: VI-Suite HBC auf macOS lauffähig machen

Stand: 12.11.2026 · Branch: `hbc_downstream`

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

### 3. Manifest aufräumen (`blender_manifest.toml`)
- `macos-x64` aus `platforms` entfernen, ebenso alle `macosx_*_x86_64`-Wheels.
- Doppelte Einträge entfernen (numpy und pybind11 aus mehreren Wheel-Ordnern).
- `cython` und `pybind11` entfernen, sie sind nur Build-Abhängigkeiten.
- `numpy` entfernen, Blender bringt es mit. Vorher prüfen, ob die ngsolve- und pyroomacoustics-Wheels
  mit Blenders numpy-Version kompatibel sind.
- `get_wheels.py` und `requirements.txt` entsprechend anpassen.

### 4. macOS-Runner (GitHub Actions) – *läuft (12.11.2026: alle Tests grün)*
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
   Die Wetterdatei im .blend (Laupheim TMYx) liegt nicht im Repo, deshalb wird ersatzweise Birmingham genutzt.
7. Berichte und Logs als Artefakt hochladen, eine Übersicht erscheint in der Job-Zusammenfassung.
   Das Zip wird nur bei manuellem Start mit `upload_zip` hochgeladen.

Lokal unter Linux mit Blender 5.1.2 getestet: Build, Installation, Smoke-Test und EnVi-Test laufen durch.
Ausnahme: pyroomacoustics, weil das Linux-Wheel lokal gebaut wird.

Voraussetzungen: Schreibzugriff der Claude GitHub App mit der Berechtigung `workflows`.
Für private Repos zählen macOS-Minuten zehnfach.

### 5. macOS-Voraussetzungen dokumentieren
- scipy-Wheel braucht macOS ≥ 14, PySide6 ≥ 13, also gilt: **mindestens macOS 14**.
  Das in `build_guide.md` und im Manifest bzw. in der Anleitung vermerken.
- Prüfen, ob Blender die `universal2`-Wheels installiert (passiert im Runner, Schritt 4).
- Die Qt-Fenster (Fortschrittsbalken) auf macOS manuell prüfen. Das geht nicht headless.

### 6. Quarantäne und Ausführungsrechte
- Nach einem Download per Browser setzt macOS `com.apple.quarantine`. Die Binaries in
  `EPFiles/darwin`, `RadFiles/darwin` und `OFFiles/darwin` können dann blockiert werden.
- Beim Laden des Add-ons auf macOS das Attribut entfernen (`xattr -dr com.apple.quarantine`) oder
  den Befehl in der Anleitung dokumentieren.

### 7. Build-Skript portabel machen
- In `build_blender_extension.sh` den Blender-Pfad über eine Variable `BLENDER` setzen
  statt fest `/home/pius/...` einzutragen, damit dasselbe Skript im Runner läuft.

## Gefundene Fehler
- `__init__.py`: Der netgen-Workaround suchte die Wheels in `/ngsolve_wheels` (Wurzelverzeichnis)
  statt im Extension-Ordner. Ist korrigiert. Ohne die Korrektur ist `netgen`/`ngsolve` nicht importierbar,
  weil das Wheel seine Pakete unter `.data/data/lib/...` ablegt und Blender diese nicht einrichtet.
- Linux: Ohne `libEGL` scheitert der PySide6-Import beim Aktivieren, und Blender entfernt danach alle Wheels.
  Auf Rechnern ohne Desktop (Server) muss `libegl1` installiert sein.

## Erledigt
- Upstream-Merge: `hbc_downstream` enthält alle Commits von `master`.
- Große Dateien: Die Wheels stehen in `.gitignore` und landen nicht im Repo.
