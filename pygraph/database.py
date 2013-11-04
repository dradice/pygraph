import sys

from PyQt4.Qt import QPoint, QSize

"""
Shared application data
"""
settings = {
        "Animation/FPS": 2,
        "Animation/Smooth": False,
        "DataEditor/Position": QPoint(0,0),
        "DataEditor/Size": QSize(500,300),
        "Plot/legendFontSize": 12,
        "Plot/legendTextLength": 30,
        "Plot/font": "Monospace",
        "Plot/titleFontSize": 12,
        "Plot/xAxisTitle": "x",
        "Plot/xGridEnabled": False,
        "Plot/xLogScale": False,
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
        "xGraph and yGraph formats (*.xg *.yg)": "xg"
        }
