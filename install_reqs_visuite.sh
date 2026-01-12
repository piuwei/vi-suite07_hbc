#! /bin/bash

# finding the path where blender gets modules from:
# in Blender console
# bpy.utils.user_resource("SCRIPTS", path="modules")
#
# e.g. >>> '/home/pius/.config/blender/4.3/scripts/modules'

# need python3.11-dev for pyroomacoustics (g++ compilation)
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11
sudo apt install python3.11-dev

BLENDER_VERSION="4.4"

python3.11 -m pip install matplotlib openimageio pyside6 --target="/home/pius/.config/blender/$BLENDER_VERSION/scripts/modules"
python3.11 -m pip install pyroomacoustics --target="/home/pius/.config/blender/$BLENDER_VERSION/scripts/modules"
python3.11 -m pip install scipy --target="/home/pius/.config/blender/$BLENDER_VERSION/scripts/modules"

# needed for numpy.core.multiarray something. Must --upgrade to overwrite preexisting numpy installs
python3.11 -m pip install numpy==1.26.4 --target="/home/pius/.config/blender/$BLENDER_VERSION/scripts/modules" --upgrade


#sudo apt install python3-matplotlib python3-kivy python3-openimageio
#python3-pyside6.qtgui python3-pyside6.qtprintsupport
#python3-pyside6.qtsvg

#
# Python: Traceback (most recent call last):
#   File "/home/pius/simulationssoftware/blender-4.3.2-linux-x64/4.3/scripts/addons_core/bl_pkg/bl_extension_ops.py", line 1481, in execute
#     cmd_batch = self.exec_command_iter(is_modal)
#                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/home/pius/simulationssoftware/blender-4.3.2-linux-x64/4.3/scripts/addons_core/bl_pkg/bl_extension_ops.py", line 2560, in exec_command_iter
#     self.exec_legacy(source_filepath)
#   File "/home/pius/simulationssoftware/blender-4.3.2-linux-x64/4.3/scripts/addons_core/bl_pkg/bl_extension_ops.py", line 2692, in exec_legacy
#     bpy.types.PREFERENCES_OT_addon_install.execute(self, bpy.context)
#   File "/home/pius/simulationssoftware/blender-4.3.2-linux-x64/4.3/scripts/startup/bl_operators/userpref.py", line 813, in execute
#     bpy.ops.preferences.addon_enable(module=mod.__name__)
#   File "/home/pius/simulationssoftware/blender-4.3.2-linux-x64/4.3/scripts/modules/bpy/ops.py", line 109, in __call__
#     ret = _op_call(self.idname_py(), kw)
#           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# RuntimeError: Fehler: numpy.core.multiarray failed to import


#
# ./blender-4.3.2-linux-x64/4.3/python/bin/python3.11 -m pip install --upgrade pip
# ./blender-4.3.2-linux-x64/4.3/python/bin/python3.11 -m pip install matplotlib --user
#
