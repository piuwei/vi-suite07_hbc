#!/usr/bin/env python3
"""Fail if a change converts the line endings of a whole text file.

The repository keeps the line endings it inherits from upstream: most of the
add-on's .py files use CRLF, the files added in this fork use LF, and some
upstream files are mixed. Converting a file (e.g. CRLF -> LF by an editor)
turns every line into a diff line and causes large conflicts when merging
from master, so it is not allowed.

A file counts as converted when its dominant line ending flips between the
base and the head revision (more than 90 % CRLF before and less than 10 %
after, or the other way round). New, deleted and binary files are ignored.

    python3 build_scripts/check_line_endings.py <base-ref> [<head-ref>]   (head defaults to HEAD)
"""

import subprocess
import sys

TEXT_SUFFIXES = (".py", ".md", ".toml", ".txt", ".sh", ".yml", ".yaml", ".cfg", ".json", ".idf", ".csv")


def git(*args):
    return subprocess.run(["git", *args], check=True, capture_output=True).stdout


def crlf_share(ref, path):
    try:
        data = git("show", f"{ref}:{path}")
    except subprocess.CalledProcessError:
        return None  # file does not exist in this revision
    if b"\0" in data[:8000]:
        return None  # binary
    lines = data.count(b"\n")
    if lines == 0:
        return None
    return data.count(b"\r\n") / lines


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    base = sys.argv[1]
    head = sys.argv[2] if len(sys.argv) > 2 else "HEAD"
    merge_base = git("merge-base", base, head).decode().strip()
    changed = git("diff", "--name-only", "--diff-filter=M", merge_base, head).decode().split()

    converted = []
    for path in changed:
        if not path.endswith(TEXT_SUFFIXES):
            continue
        before, after = crlf_share(merge_base, path), crlf_share(head, path)
        if before is None or after is None:
            continue
        if (before > 0.9 and after < 0.1) or (before < 0.1 and after > 0.9):
            converted.append((path, before, after))

    for path, before, after in converted:
        print(f"::error file={path}::line endings converted ({before:.0%} -> {after:.0%} CRLF). "
              f"Keep the file's original line endings (see DEVELOPMENT.md, 'Zeilenenden').")
    print(f"checked {len(changed)} changed files, {len(converted)} with converted line endings")
    return 1 if converted else 0


if __name__ == "__main__":
    sys.exit(main())
