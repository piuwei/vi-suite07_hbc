"""Plausibility check for EPW weather files.

    python3 tests/check_weather_files.py [file.epw ...]

Without arguments all EPW files in EPFiles/Weather are checked.
Runs without Blender. Exit code 1 if a file fails a check.

Checks per file:
- 8760 (or 8784) hourly data rows
- dry-bulb temperature within -60 ... 55 °C, no missing values (99.9)
- no hour-to-hour temperature jump larger than MAX_JUMP K
- relative humidity within 0 ... 100 %
- dew point not above dry-bulb temperature (tolerance 0.5 K)
- global horizontal irradiance within 0 ... 1400 W/m²
"""

import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T_RANGE = (-60.0, 55.0)
# Real data reaches about 15 K/h (Fairbanks, winter inversion broken up by wind).
MAX_JUMP = 20.0
GHI_MAX = 1400.0
MAX_LISTED = 5


def check(path):
    """Return a list of problems found in one EPW file."""
    with open(path, encoding="latin-1") as fh:
        lines = fh.read().splitlines()
    rows = [l.split(",") for l in lines[8:] if l.strip()]
    problems = []

    if len(rows) not in (8760, 8784):
        problems.append(f"{len(rows)} data rows, expected 8760 or 8784")

    issues = {"temperature out of range": [], "temperature jump": [], "humidity out of range": [],
              "dew point above temperature": [], "irradiance out of range": [], "unreadable row": []}
    prev = None
    for r in rows:
        stamp = f"{int(r[1]):02d}-{int(r[2]):02d} {int(r[3]):02d}h" if len(r) > 3 else "?"
        try:
            t, td, rh, ghi = float(r[6]), float(r[7]), float(r[8]), float(r[13])
        except (IndexError, ValueError):
            issues["unreadable row"].append(stamp)
            continue
        if not T_RANGE[0] <= t <= T_RANGE[1]:
            issues["temperature out of range"].append(f"{stamp}: {t}")
        if prev is not None and abs(t - prev) > MAX_JUMP:
            issues["temperature jump"].append(f"{stamp}: {prev} -> {t}")
        if not 0 <= rh <= 100:
            issues["humidity out of range"].append(f"{stamp}: {rh}")
        if td > t + 0.5 and td < 99:
            issues["dew point above temperature"].append(f"{stamp}: Td {td} > T {t}")
        if not 0 <= ghi <= GHI_MAX:
            issues["irradiance out of range"].append(f"{stamp}: {ghi}")
        prev = t

    for name, hits in issues.items():
        if hits:
            more = f" (+{len(hits) - MAX_LISTED} more)" if len(hits) > MAX_LISTED else ""
            problems.append(f"{name}, {len(hits)}x: " + "; ".join(hits[:MAX_LISTED]) + more)
    return problems


def main(paths):
    paths = paths or sorted(glob.glob(os.path.join(ROOT, "EPFiles", "Weather", "*.epw")))
    if not paths:
        print("no EPW files found")
        return 1
    failed = 0
    for p in paths:
        problems = check(p)
        print(f"[{'FAIL' if problems else 'PASS'}] {os.path.relpath(p, ROOT)}")
        for pr in problems:
            print(f"       {pr}")
        failed += bool(problems)
    print(f"\n{len(paths)} files, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
