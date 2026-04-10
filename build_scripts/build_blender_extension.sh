#!/usr/bin/bash

## might help to install in conda / python venv:
# pip install pyroomacoustics 
# pip install ngsolve 

# TODAY=$(date '+%y%m%d')
VERSION="v003"
TARGET_PATH="../assets/blender_extensions/Blender-5.1.0/vi-suite_HBC_${VERSION}.zip"

# change to desired blender executable
/home/pius/simulationssoftware/blender-5.1.0-linux-x64/blender \
  --command extension build \
  --source-dir ../ \
  --output-filepath ${TARGET_PATH} \
  --split-platforms \