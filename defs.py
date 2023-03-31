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

#drivers
GPKG_DRIVER = "GPKG"
SHAPE_DRIVER = "shp"

# message strings
msg_value_error = "Please enter a valid integer."
msg_value_error_float = "Please enter a valid float value."
msg_processing = "Processing data"
SQ = "\u00b2"

# colours
RED = "\033[1;31m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[1;34m"
MAGENTA = "\033[1;35m"
CYAN = "\033[1;36m"
HEADER = "\033[95m"
OKBLUE = "\033[94m"
OKCYAN = "\033[96m"
OKGREEN = "\033[92m"
WARNING = "\033[93m"
FAIL = "\033[91m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
RST = "\033[0m"

# attribute names
CLASS = "CLASS_TYPE"
GROUP = "GROUP_"
ID = "ID"
NAME = "NAME"
PUID = "GRID_ID"
AREA_X = "AREA_X"
SPECIES = "species"
PU = "pu"
AMOUNT = "amount"

TARGET_CRS = (
    'PROJCS["EPSG_42304_LCC",GEOGCS["NAD83",DATUM'
    '["North_American_Datum_1983",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY'
    '["EPSG","7019"]],AUTHORITY["EPSG","6269"]],PRIMEM["Greenwich",0],UNIT'
    '["Degree",0.0174532925199433]],PROJECTION["Lambert_Conformal_Conic_2SP"],PARAMETER'
    '["latitude_of_origin",49],PARAMETER["central_meridian",-95],PARAMETER'
    '["standard_parallel_1",49],PARAMETER["standard_parallel_2",77],PARAMETER'
    '["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY'
    '["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH]]'
)
