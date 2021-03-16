#!/bin/bash

export PYTHONPATH=$PYTHONPATH:$PWD

MAKEICNS=/opt/local/bin/makeicns
PYINSTALLER=$HOME/Library/Python/3.8/bin/pyinstaller

mkdir -p export/macOS
cd export/macOS

$MAKEICNS \
    -in ../../pygraph.jpg \
    -out pygraph.icns || exit 1

$PYINSTALLER \
    --clean \
    --hidden-import=h5py.h5ac \
    --hidden-import=appdirs \
    --hidden-import=packaging \
    --hidden-import=packaging.requirements \
    --icon=pygraph.icns \
    --runtime-hook=../../rthook_pyqt4.py \
    --windowed \
    --onefile \
    --strip \
    ../../bin/pygraph || exit 1

hdiutil create \
    -volname pygraph \
    -srcfolder dist/pygraph.app \
    -ov -format UDZO pygraph.dmg
