# -*- coding: utf-8 -*-
"""
defs.py

This file contains general definitions for the planning.py script

@author: Mitch Albert

"""


# filedialog file types
ft_shapefile = ("Shapefile", "*.shp")
ft_geo_package = ("GeoPackage ", "*.gpkg")
ft_geodatabase = ("File Geodatabase", "*.gdb")
ft_csv = ("Comma-separated values", "*.csv")
ft_json = ("Json", ("*.geojson", "*.json"))
ft_kml = ("Keyhole Markup Language", "*.KML")
ft_any = ("All files", "*.*")
ft_none = ("Any", "")
ft_standard = [ft_shapefile, ft_geo_package, ft_any]
ft_standard_save = [ft_csv, ft_shapefile]
ft_all = [ft_any, ft_csv, ft_json, ft_shapefile, ft_geo_package, ft_kml]

# message strings
msg_value_error = "Please enter a valid integer."
msg_value_error_float = "Please enter a valid float value."
SQ = "\u00b2"

# colours
RED = "\033[1;31m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[1;34m"
MAGENTA = "\033[1;35m"
CYAN = "\033[1;36m"
RST = "\033[0m"

# attribute names
CLASS = "CLASS_TYPE"
GROUP = "GROUP_"
ID = "ID"
NAME = "NAME"
PUID = "GRID_ID"
AREA_X = "AREA_X"

# other
URL_INDEX = "http://127.0.0.1:5000/"
URL_INPUT = "http://127.0.0.1:5000/input"
URL_SHUTDOWN = "http://127.0.0.1:5000/shutdown"
