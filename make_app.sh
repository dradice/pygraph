#!/bin/bash

export PYTHONPATH=$PYTHONPATH:$PWD

MAKEICNS=/opt/local/bin/makeicns
PYINSTALLER=/opt/local/Library/Frameworks/Python.framework/Versions/2.7/bin/pyinstaller

mkdir -p export/OSX
cd export/OSX

$MAKEICNS \
    -in ../../pygraph.jpg \
    -out pygraph.icns || exit 1

$PYINSTALLER \
    --clean \
    --hidden-import=h5py.h5ac \
    --icon=pygraph.icns \
    --runtime-hook=../../rthook_pyqt4.py \
    --windowed \
    --onefile \
    --strip \
    ../../bin/pygraph || exit 1
