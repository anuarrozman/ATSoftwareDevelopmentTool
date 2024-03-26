#!/bin/bash

# Install esptool
pip install esptool --break-system-packages

# Install pyinstaller
pip install pyinstaller --break-system-packages

# Install hidapi
pip install hidapi --break-system-packages

# Install hid
pip install hid --break-system-packages

export ProdTool_Path = ${HOME}/ATSoftwareDevelopmentTool/Sprint14-Prototype/

# Build the project
pyinstaller --onefile main.py --hidden-import esptool --hidden-import pyserial --hidden-import hidapi --distpath ${ProdTool_Path}

