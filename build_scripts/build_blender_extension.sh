#!/usr/bin/bash

## might help to install in conda / python venv:
# pip install pyroomacoustics 
# pip install ngsolve 

TODAY=$(date '+%y%m%d')

# change Path to desired blender executable
/home/pius/simulationssoftware/blender-5.1.0-linux-x64/blender \
  --command extension build \
  --source-dir ../ \
  --output-filepath ../assets/vi-suite_HBC_${TODAY}.zip \
  --split-platforms \