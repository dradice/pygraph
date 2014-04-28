#!/bin/bash

export PYTHONPATH=$PYTHONPATH:$PWD

MAKEICNS=/opt/local/bin/makeicns
PYINSTALLER=/opt/local/Library/Frameworks/Python.framework/Versions/2.7/bin/pyinstaller 

mkdir -p export/OSX
cd export/OSX

$MAKEICNS \
    -in ../../pygraph.jpg \
    -out pygraph.icns

$PYINSTALLER \
    --hidden-import=h5py.h5ac \
    --icon=pygraph.icns \
    --windowed \
    --onefile \
    --strip \
    ../../bin/pygraph
