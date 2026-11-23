#!/usr/bin/env bash
# Decide whether a scheduled (nightly) test run is needed (used by macos.yml/windows.yml).
#
# Compares the current commit with the commit of the last successful scheduled run of
# the same workflow. Writes run=true to $GITHUB_OUTPUT if files changed that are not
# ignored for the tests (same list as paths-ignore in the workflows), else run=false.
# When in doubt (no earlier run, API error, commit not found) it writes run=true.
#
#   GH_TOKEN=... bash build_scripts/ci_changed_since_last_run.sh macos.yml
set -uo pipefail

workflow="$1"
output="${GITHUB_OUTPUT:-/dev/stdout}"

decide() {
    echo "$2"
    echo "run=$1" >> "$output"
    exit 0
}

last="$(gh api "repos/${GITHUB_REPOSITORY}/actions/workflows/${workflow}/runs?event=schedule&branch=${GITHUB_REF_NAME}&status=success&per_page=1" \
    --jq '.workflow_runs[0].head_sha // empty' 2>&1)" \
    || decide true "Could not read earlier runs (${last}), running the tests"

[ -n "$last" ] || decide true "No successful scheduled run yet, running the tests"
git cat-file -e "${last}^{commit}" 2>/dev/null \
    || decide true "Commit ${last} of the last run not found, running the tests"

# keep in sync with paths-ignore in macos.yml / windows.yml
changed="$(git diff --name-only "$last" HEAD | grep -vE '\.md$|^docs/|^\.gitignore$|^Licenses/' || true)"

if [ -n "$changed" ]; then
    echo "Changed since ${last}:"
    echo "$changed" | sed 's/^/   /'
    decide true "Running the tests"
fi
decide false "No relevant changes since the last successful run (${last}), skipping the tests"
