# Build-Guide (Entwicklung)

Anleitung für Entwickler: lokal testen, Extension bauen, Updates aus Upstream holen, Release.
Für Nutzer siehe [README.md](../README.md), für Tests, Regeln und TODOs siehe [development.md](development.md).

## 1. Lokal testen: geänderte Dateien in die installierte Extension kopieren

Die Extension ist nach der Installation hier entpackt (`<x.y>` = Blender-Version, z. B. `5.3`):

| System | Ordner |
|---|---|
| Linux | `~/.config/blender/<x.y>/extensions/user_default/vi_suite_HBC/` |
| macOS | `~/Library/Application Support/Blender/<x.y>/extensions/user_default/vi_suite_HBC/` |
| Windows | `%APPDATA%\Blender Foundation\Blender\<x.y>\extensions\user_default\vi_suite_HBC\` |

Für schnelle Tests reicht es, die geänderten `.py`-Dateien dorthin zu kopieren und Blender neu zu starten,
z. B. unter Linux:

```sh
cp -u *.py ~/.config/blender/5.3/extensions/user_default/vi_suite_HBC/
```

Bei Änderungen an Wheels, Manifest oder Programmdateien (`EPFiles`, `RadFiles`, `OFFiles`) die Extension
neu bauen und installieren (Abschnitt 3).

## 2. Wheels holen

Die Python-Pakete (Wheels) liegen nicht im Repo. `get_wheels.py` lädt sie für alle Plattformen von PyPI
(ohne Conda, Python ≥ 3.11, aus jedem Verzeichnis):

```sh
python3 build_scripts/get_wheels.py --clean
```

- `--check` vergleicht mit der Wheel-Liste in `blender_manifest.toml` und zeigt neuere Versionen.
- `--write` ersetzt die Wheel-Liste im Manifest (danach alle Blender-Versionen testen, siehe Abschnitt 5).
- Welche Pakete geladen werden, steht in `build_scripts/requirements.txt`. `PySide6-Essentials` ist auf
  6.11.0 festgelegt: Neuere Versionen enthalten einen Pfad, der unter Windows zu lang ist. Das Skript bricht
  in solchen Fällen mit Fehler ab.

## 3. Extension bauen

```sh
BLENDER=/pfad/zu/blender bash build_scripts/build_blender_extension.sh
```

- Baut je ein Zip pro Plattform (`--split-platforms`) nach
  `assets/blender_extensions/Blender-<blender-version>/vi-suite_HBC_v<version>-<plattform>.zip`,
  z. B. `vi-suite_HBC_v0.0.5-macos_arm64.zip` (Ordner per `OUT_DIR=...` änderbar).
  Dafür müssen die Wheels aller Plattformen da sein (Abschnitt 2).
- Installieren in Blender: *Edit → Preferences → Get Extensions → Install from Disk*.
- Nicht im Zip: `tests/`, `docs/`, `build_scripts/`, `.github/`, `vi07.pdf` (siehe `paths_exclude_pattern`
  in `blender_manifest.toml`).

Für einen einzelnen Testbuild ist es oft einfacher, in GitHub *Actions → macOS test / Linux test /
Windows test → Run workflow* mit `upload_zip` zu starten. Das Zip liegt dann im Artefakt
`vi-suite_HBC-<plattform>-extension`.

## 4. Updates aus Upstream übernehmen

`master` ist ein Spiegel von Upstream (rgsouthall). Ablauf:

1. `master` mit Upstream abgleichen: auf GitHub im Repo auf `master` *Sync fork* klicken.
2. `master` in einen Arbeits-Branch mergen und als Pull Request nach `hbc_downstream` stellen, damit die
   CI den Stand auf allen Plattformen testet:
   ```sh
   git fetch origin
   git checkout -b merge-master origin/hbc_downstream
   git merge origin/master
   ```
   Konflikte lösen, committen, pushen und den PR anlegen.
3. Danach prüfen:
   - **Zeilenenden:** Die Upstream-Dateien behalten ihre Zeilenenden (meist CRLF). Beim Lösen von Konflikten
     darf der Editor sie nicht umstellen. Die Prüfung `checks.yml` im PR meldet das, lokal:
     `python3 build_scripts/check_line_endings.py origin/hbc_downstream`
   - **EnergyPlus (macOS):** Bringt `master` eine neue EnergyPlus-Binary nach `EPFiles/darwin`, auf einem Mac
     `bash build_scripts/fix_energyplus_rpath_macos.sh` ausführen und das Ergebnis committen.
     Die macOS-CI schlägt fehl, solange das fehlt.
   - **Manifest:** Neue Python-Abhängigkeiten aus Upstream in `build_scripts/requirements.txt` ergänzen und
     die Wheel-Liste aktualisieren (Abschnitt 2, `--write`).

## 5. Release

Ein Release mit je einem Zip für macOS arm64, Linux x64 und Windows x64 entsteht automatisch, wenn ein
Versions-Tag gepusht wird (`.github/workflows/release.yml`).

1. Vorher alle Blender-Versionen testen: *Actions → Blender versions → Run workflow*
   (Standard: Mindestversion bis neueste Version, siehe [development.md](development.md)).
2. `version` in `blender_manifest.toml` erhöhen, per Pull Request nach `hbc_downstream` mergen.
3. Tag auf den Merge setzen und pushen (`<version>` = Wert aus dem Manifest, z. B. `0.0.5`):
   ```sh
   git checkout hbc_downstream && git pull
   git tag v<version>
   git push origin v<version>
   ```
4. Der Workflow prüft, dass Tag und Manifest-Version übereinstimmen, baut und testet alle Plattformen
   (Linux-Zip auf Ubuntu 24.04 und 26.04) und legt das Release mit `vi-suite_HBC_v<version>-<plattform>.zip`
   an. Die Notizen enthalten Installation, Voraussetzungen und die Liste der PRs.
5. Optional: Im Release über *Edit release* einen kurzen Abschnitt „Fixes“ in Klartext ergänzen.

Das Release nicht vorher von Hand auf GitHub anlegen: Dann schlägt der Workflow fehl, weil das Release schon
existiert. Ohne Tag baut und testet *Actions → Release → Run workflow* alle Plattformen und lädt die Zips nur
als Artefakte hoch.

## 6. Plattform-Hinweise

**macOS**
- Nur Apple Silicon, macOS 14 oder neuer (die scipy- und PySide6-Wheels brauchen macOS 14; Blender 5 läuft
  nicht auf Intel-Macs, deshalb gibt es keinen `macos-x64`-Build).
- Die mitgelieferte EnergyPlus-Binary ist für macOS repariert (rpath), siehe Abschnitt 4.
- Quarantäne: Dateien aus einem Browser-Download tragen `com.apple.quarantine`. Das Add-on entfernt das
  Attribut beim Laden aus seinen Programmordnern. Von Hand:
  ```sh
  xattr -dr com.apple.quarantine ~/Library/Application\ Support/Blender/<x.y>/extensions/user_default/vi_suite_HBC
  ```
- Hintergründe: [macos_plan.md](macos_plan.md)

**Linux**
- Das Zip braucht glibc ≥ 2.34 (PySide6 ist manylinux_2_34), z. B. Ubuntu 22.04 oder neuer.
- Blender mit PySide6 braucht die Systembibliothek `libegl1`. Fehlt sie, scheitert das Aktivieren des Add-ons,
  und Blender entfernt alle Wheels wieder.

**Windows**
- Pfade im Extension-Ordner dürfen 260 Zeichen nicht überschreiten (siehe Abschnitt 2, PySide6).
