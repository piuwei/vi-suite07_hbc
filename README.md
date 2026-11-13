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
