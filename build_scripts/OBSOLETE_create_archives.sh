#! /bin/bash

# OBSOLETE !!!

# Initialize variables
prefix="vi-suite07_hbc_260119"
branch="hbc_downstream"
full_archive=false
tiny_archive=false
help_flag=false

# Parse command-line arguments using a loop and case statement
while [[ $# -gt 0 ]]; do
  case "$1" in
    --full)
      full_archive=true
      shift
      ;;
    --tiny)
      tiny_archive=true
      shift
      ;;
    --all)
      full_archive=true
      tiny_archive=true
      shift
      ;;
    -h | --help)
      help_flag=true
      shift
      ;;
    *)
      echo "Error: Unknown option '$1'"
      exit 1
      ;;
  esac
done
# Display help message if requested or if no size option is provided
if [[ "$help_flag" == true ]] || [[ "$full_archive" == false && "$small_archive" == false && "$tiny_archive" == false ]]; then
  cat <<EOF
Usage: $0 [OPTIONS]

Creates Git archives of different sizes.  If no size option is specified,
this help message will be displayed.

Options:
  --full   Create a full archive (all files).
  --tiny   Create a tiny archive (only .py files, excludes large files).
  --all    Create all of the above archives.
  -h, --help Display this help message.

Examples:
  $0 --full             # Creates only the full archive.
  $0 --all              # Creates full, small, and tiny archives.
  $0                   # Displays this help message.
EOF

  # Exit after displaying help, whether it was explicitly requested or the default
  exit 0
fi

# Display help message if requested or if no size option is provided
if [[ "$help_flag" == true ]] || [[ "$full_archive" == false && "$small_archive" == false && "$tiny_archive" == false ]]; then
  cat <<EOF
Usage: $0 [OPTIONS]

Creates Git archives of different sizes.  If no size option is specified,
this help message will be displayed.

Options:
  --full   Create a full archive (all files).
  --tiny   Create a tiny archive (only .py files, excludes large files).
  -h, --help Display this help message.

Examples:
  $0 --full             # Creates only the full archive.
  $0 --tiny    # Creates both small and tiny archives.
EOF

  # Exit after displaying help, whether it was explicitly requested or the default
  exit 0
fi

# Create archives based on the selected options

if [[ "$full_archive" == true ]]; then
  echo "Creating full archive..."
  git archive --format=zip --prefix="$prefix"/ -o assets/"$prefix"_"$branch"_full.zip "$branch"
fi

if [[ "$tiny_archive" == true ]]; then
  echo "Creating tiny archive..."
  git archive --worktree-attributes --format=zip --prefix="$prefix"_tiny/ -o assets/"$prefix"_"$branch"_tiny.zip "$branch" *.py
fi

echo "Done."
exit 0
