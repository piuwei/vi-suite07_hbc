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

User manual (not included in the extension zip): [vi07.pdf](https://github.com/piuwei/vi-suite07_hbc/blob/hbc_downstream/vi07.pdf)

Requirements:

- Blender 5.1 or newer (tested with 5.1.2, 5.2.4 LTS and 5.3.0)
- Windows x64, Linux x64 (glibc 2.34 or newer, e.g. Ubuntu 22.04, 24.04, 26.04) or macOS 14 (Sonoma) or newer on Apple Silicon.
  Intel Macs are not supported (Blender 5 runs on Apple Silicon only).

## Development

- Development notes (tests, release, TODO list): [DEVELOPMENT.md](DEVELOPMENT.md)
- Building the extension: [build_guide.md](build_guide.md)
