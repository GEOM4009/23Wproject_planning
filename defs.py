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
DEFAULT_RESULTS_FILE_NAME = "marxan_results"

# drivers
GPKG_DRIVER = "GPKG"
SHAPE_DRIVER = "shp"

# Message formatting
COLOUR = False
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

if not COLOUR:
    RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = HEADER = OKBLUE = OKCYAN = OKGREEN = WARNING = FAIL = BOLD = UNDERLINE = RST = ""

# message strings
msg_value_error = "Please enter a valid integer."
msg_value_error_float = "Please enter a valid float value."
msg_processing = "Processing data"
ABORT = "(Use 'ctrl + c' to abort)\n"
SQ = "\u00b2"
intro_title = f"{BOLD}***Conservation Feature Planning Data Preparation***{RST}"
intro_message = f"""
     {intro_title}
    Please use the menus to prepare your data accordingly.
    The first step will be to select a CRS that all files
    will be projected to. You will then be able to create
    or load a planning unti grid. Note if you load an
    existing planning unit grid its CRS will be used
    instead if it is in a projected CRS. You will then be
    able to load a conservation feature layer(s), and filter
    them as required. After loading a planning unit grid and
    conservation features you will be able to calculate
    the conservation feature area within each planning
    unit. Finally, you will be can save the results to a
    file, inlcuding the grid, the conservation features
    used, and a csv file with the results. Options
    indicated with square brackets [#] are the default,
    and will be selected if you press enter without value.
    """


# default option values
# If you change these, you must also change the corresponding
# default [#] indicators in the menu
DEFAULT_INPUT = ''
DEFAULT_CRS_INPUT = 1
DEFAULT_GRID_INPUT = 1
DEFAULT_LOAD_CONSERVATION_INPUT = 1
DEFAULT_QUEURY_INPUT = 1
DEFAULT_PLOT_INPUT = 9
DEFAULT_QUIT = 'n'


# attribute names
ID = "ID"       # id field name for conservation features, this must be present in the conservation feature layers

CLASS = "CLASS_TYPE"
GROUP = "GROUP_"
NAME = "NAME"
PUID = "GRID_ID"  # grid id field name for planning unit grid, this must be present in the planning unit grid
GEOMETRY = "geometry"
MAP_COLUMN = "ID"

# marxan csv header names
SPECIES = "species"
PU = "pu"
AMOUNT = "amount"



# Units
# Prefixes
M = "m"
METERS = "meters"
M_FACTOR = 1
H = "h"
HECTO = "hecto"
HM_FACTOR = 100
K = "k"
KILO = "kilo"
KM_FACTOR = 1000

# Suffixes
M_SQ = M + SQ
METERS_SQ = METERS + SQ
HM = H + M

HECTOMETERS = HECTO + METERS
HECTOMETERS_SQ = HECTOMETERS + SQ
HM_SQ = H + M + SQ

# HECTARES = "hectares"
# HA = "ha"
# HA_FACTOR = HM_FACTOR

KM = K + M
KILOMETERS = KILO + METERS
KILIOMETERS_SQ = KILOMETERS + SQ
KM_SQ = KM + SQ

DEFAULT_UNIT_FACTOR = M_FACTOR
DEFAULT_UNITS_SQ = METERS_SQ
DEF_UNITS_SQ = M_SQ

SUFFIX_DICT = {M_SQ: M_FACTOR, HM_SQ: HM_FACTOR, KM_SQ: KM_FACTOR}

ESRI102001 = "ESRI:102001"
# ESRI102001 = 'PROJCS["Canada_Albers_Equal_Area_Conic",GEOGCS["NAD83",DATUM["North_American_Datum_1983",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],AUTHORITY["EPSG","6269"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4269"]],PROJECTION["Albers_Conic_Equal_Area"],PARAMETER["latitude_of_center",40],PARAMETER["longitude_of_center",-96],PARAMETER["standard_parallel_1",50],PARAMETER["standard_parallel_2",70],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["ESRI","102001"]]'
TARGET_CRS = ESRI102001  # Canada_Albers_Equal_Area_Conic
