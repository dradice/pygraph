import sys

import platform
from PyQt5.QtCore import QPoint, QSize

"""
Shared application data
"""
settings = {
        "Animation/FPS": 2.0,
        "Animation/MaxNFrames": 10000,
        "Animation/Smooth": False,
        "DataEditor/Position": QPoint(0,0),
        "DataEditor/Size": QSize(500,300),
        "MainWindow/Position": QPoint(0,0),
        "MainWindow/Size": QSize(600,400),
        "PyGraph/Debug": False,
        "Plot/font": "Monospace",
        "Plot/legendFontSize": 8,
        "Plot/legendTextLength": 30,
        "Plot/maxFramesForPlotAll": 100,
        "Plot/maxZoomFactor": 50.0,
        "Plot/titleFontSize": 10,
        "Plot/xAxisTitle": "x",
        "Plot/xGridEnabled": False,
        "Plot/xLogScale": False,
        "Plot/xLogScaleMin": sys.float_info.epsilon,
        "Plot/xMin": 0,
        "Plot/xMax": 1,
        "Plot/yAxisTitle": "y",
        "Plot/yGridEnabled": False,
        "Plot/yLogScale": False,
        "Plot/yLogScaleMin": sys.float_info.epsilon,
        "Plot/yMin": 0,
        "Plot/yMax": 1,
        "PlotSettings/Position": QPoint(0,0),
        "PlotSettings/Size": QSize(500,300),
        "ToolBar/IconSize": QSize(32,32)
        }

# Use a different font size on Mac OS X
if platform.system() == 'Darwin':
    settings['Plot/legendFontSize'] = 12
    settings['Plot/titleFontSize']  = 12

colors = [
        "Blue",
        "Red",
        "Green",
        "Purple",
        "Orange",
        "Navy",
        "Silver",
        "DarkCyan",
        "HotPink",
        "Lime",
        "Chocolate",
        "BlueViolet",
        "DarkRed",
        "SteelBlue",
        "Indigo"
        ]

formats = {
        "Carpet ASCII (*.?.asc)": "CarpetIOASCII",
        "Carpet Scalar (*.asc)": "CarpetIOScalar",
        "Carpet HDF5 (*.h5)": "h5",
        "Legagy PyGraph HDF5 (*.pyg)": "pygraph",
        "PyGraph HDF5 (*.h5)": "pygraph",
        "xGraph and yGraph formats (*.xg *.yg)": "xg"
        }

status = ""

def debug_print(msg):
    if settings["PyGraph/Debug"]:
        print(msg)
