import sys

"""
Shared application data
"""
settings = {
        "Animation/FPS": 2,
        "Plot/legendFontSize": 8,
        "Plot/legendTextLength": 30,
        "Plot/font": "Monospace",
        "Plot/titleFontSize": 10,
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
        "Plot/yMax": 1
        }

colors = [
        "Black",
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
        "Carpet ASCII (*.asc)": "asc",
        "Carpet HDF5 (*.h5)": "h5",
        "xGraph and yGraph formats (*.xg *.yg)": "xg"
        }
