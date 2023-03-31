# -*- coding: utf-8 -*-
"""
planning.py
Authors: Mitch, Lucas, Ethan, Nata, Winaa

This file contains the main script for the GEOM4009 planning project.
It contains the main menu and all the functions for the different the
different steps of the data and planning process.

NOTE: This script must be run in the geom4009 environment, but will require
      the installation of the following additional packages:

    conda install -c conda-forge tk  --> provides the tkinter GUI

TODO: Get user input to set CRS for the project
TODO: Confirm with client if there will be any use case for an argument parser
TODO: Add additional error handling for the different functions

"""
# Import modules
from util import *
from defs import *
import os

os.environ["USE_PYGEOS"] = "0"
from time import time

from shapely.geometry import Polygon
import shapely
from math import pi, cos, sqrt
import math

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

from tqdm import tqdm
from multiprocessing import Pool

import numpy as np
import psutil
from functools import partial
import pyproj


# Global Variables
run_tests = False
verbose = True
CORES = psutil.cpu_count(logical=False)
target_crs = TARGET_CRS
rectangular_grid = False



# %% Obtain the CRS from the user

def crs():
    """
  Author: Ethan
  The user enters the crs and if it is alber equal area then they have to enter the required coordinates which it will be processed into the crs formula to create the crs which will be
  saved as a variable called target_crs. This will make it so the rest of the functions can call this function to keep a consistent CRS. 
  
  Parameters:
      
      target crs: the formula for the crs. Then to use the crs pyproj is needed. 

    """


    # Ask user for CRS
    crs = input("Enter CRS: ")

    if crs == "Albers Equal Area":
    # Get inputs from user
        lat_1 = float(input("Enter Latitude of the first standard parallel: "))
        lat_2 = float(input("Enter Latitude of the second standard parallel: "))
        lon_0 = float(input("Enter Longitude of the central meridian: "))
        lat_0 = float(input("Enter Latitude of the projection origin: "))

    # Create CRS
    target_crs = pyproj.Proj(
        "+proj=aea +lat_1={} +lat_2={} +lon_0={} +lat_0={} +datum=WGS84 +units=m +no_defs".format(
            lat_1, lat_2, lon_0, lat_0
        )
    )
    else:
        # Use the input CRS
        target_crs = pyproj.Proj(crs)




# %% create a planning unit grid
def create_hexagon(l, x, y):
    """
    Author:Kadir Şahbaz
    Create a hexagon centered on (x, y)
    :param l: length of the hexagon's edge
    :param x: x-coordinate of the hexagon's center
    :param y: y-coordinate of the hexagon's center
    :return: The polygon containing the hexagon's coordinates
    Source:https://gis.stackexchange.com/questions/341218/creating-a-hexagonal-grid-of-regular-hexagons-of-definite-area-anywhere-on-the-g
    """
    c = [[x + math.cos(math.radians(angle)) * l, y + math.sin(math.radians(angle)) * l] for angle in range(0, 360, 60)]
    return Polygon(c)


def create_hexgrid(bbx, side):
    """
    Author:Kadir Şahbaz
    returns an array of Points describing hexagons centers that are inside the given bounding_box
    :param bbx: The containing bounding box. The bbox coordinate should be in Webmercator.
    :param side: The size of the hexagons'
    :return: The hexagon grid
    Source:https://gis.stackexchange.com/questions/341218/creating-a-hexagonal-grid-of-regular-hexagons-of-definite-area-anywhere-on-the-g
    """
    grid = []
    v_step = math.sqrt(3) * side
    h_step = 1.5 * side

    x_min = min(bbx[0], bbx[2])
    x_max = max(bbx[0], bbx[2])
    y_min = min(bbx[1], bbx[3])
    y_max = max(bbx[1], bbx[3])

    h_skip = math.ceil(x_min / h_step) - 1
    h_start = h_skip * h_step

    v_skip = math.ceil(y_min / v_step) - 1
    v_start = v_skip * v_step

    h_end = x_max + h_step
    v_end = y_max + v_step

    if v_start - (v_step / 2.0) < y_min:
        v_start_array = [v_start + (v_step / 2.0), v_start]
    else:
        v_start_array = [v_start - (v_step / 2.0), v_start]

    v_start_idx = int(abs(h_skip) % 2)

    c_x = h_start
    c_y = v_start_array[v_start_idx]
    v_start_idx = (v_start_idx + 1) % 2
    while c_x < h_end:
        while c_y < v_end:
            grid.append((c_x, c_y))
            c_y += v_step
        c_x += h_step
        c_y = v_start_array[v_start_idx]
        v_start_idx = (v_start_idx + 1) % 2

    return grid


def create_planning_unit_grid() -> gpd.GeoDataFrame:
    """
    Author: Lucas
    This function will take user input to create a hexagonal planning
    grid that is defined by a central coordinate, cell resolution,
    and grid height and width. A unique Planning unit ID is then given
    to each hexagon and the final grid can be output to a shapefile.
    It can also create this grid using other methods, such as taking a
    shapefile as input, the CRS and the bounds of that file will be
    determined and used to create the planning grid. Additionally a
    previously created grid can be input by the user
    Parameters
    ----------
    Area: float
        Size of grid cell that the user will use, the units will be
        the same units as the CRS that the user specifies
    grid_size_x: float
        width of the grid
    grid_size_y: float
        height of the grid
    grid_lat: float
        y coordinate for center of grid
    grid_lon: float
        x coordinate for center of grid
    Returns
    -------
    TYPE
        Description

    """

    planning_unit_grid = gpd.GeoDataFrame()

    while True:
        try:
            selection = int(
                input(
                    """
    Create Planning Unit Grid
        1 Create Grid from Shape File extents
        2 Load existing Grid from File
        3 Create Grid from User Input
        9 Return to Main Menu
    >>> """
                )
            )
        except ValueError:
            print_warning_msg(msg_value_error)
            continue

        # 1 Create Grid from Shape File extents
        if selection == 1:
            #user can enter the file that will define the bounds and cell area
            file = get_file(title="Select a file to load the extents from")
            Area = get_user_float("Grid Cell Area (Meters Squared):")
            Prj = file.crs
            box = file.total_bounds
            #edge length of individual hexagon is calculated using the area
            edge = math.sqrt(Area**2 / (3 / 2 * math.sqrt(3)))
            hex_centers = create_hexgrid(box, edge)
            #Empy list is created that will contain the hexagons
            hexagons = []
            #centre points are iterated through the function that creates a
            #hexagon around each of them and adds it to the list
            for center in hex_centers:
                hexagons.append(create_hexagon(edge, center[0], center[1]))
            #Geometry list is turned into a geodataframe
            planning_unit_grid = gpd.GeoDataFrame(geometry=hexagons, crs=Prj)
            # unique PUID is assigned to each hexagon
            planning_unit_grid["PUID"] = planning_unit_grid.index + 1
            planning_unit_grid.name = "Planning Unit Grid"
            # planning_unit_grid.to_file("planning_unit_grid.shp")
            break

        # 2 Load existing Grid from File
        elif selection == 2:
            file = get_file(title="Select a file to load the grid from")
            if file:
                planning_unit_grid = load_files(file, verbose)
                # TODO: This is a hack to get the global target_crs, should enable
                #      an option to do it this way or ask the user which crs to use.
                #      This crs should checked to see if it is projected or not.
                global target_crs
                target_crs = planning_unit_grid.crs
                if verbose:
                    print_info(f"Hex area: {round(planning_unit_grid.geometry.area[0])}")
            else:
                print_warning_msg("No file loaded, please try again.")
                continue
            break

        # 3 Create Grid from User Input
        elif selection == 3:
            # The inputs below will get the information needed to
            # create a boundary that will be filled with the hexagons as
            # well as define the hexagon cell size
            Area = get_user_float("Grid Cell Area (Meters Squared):")
            grid_size_x = get_user_float("Grid Size X (m): ")
            grid_size_y = get_user_float("Grid Size Y (m): ")
            grid_lat = get_user_float("Latitude of grid anchor point (dd): ")
            grid_lon = get_user_float("Longitude of grid anchor point (dd): ")
            # Half of the grid width and height can be added to the central
            # coordinate to create a study area that meets the criteria
            xdiff = grid_size_x / 2
            ydiff = grid_size_y / 2
            #Bounds of the area of interest are created by converting meters
            #to degrees so that the distance can be determined using coordinates
            xmax = grid_lon + (180 / pi) * (xdiff / 6378137) / cos(grid_lat)
            xmin = grid_lon - (180 / pi) * (xdiff / 6378137) / cos(grid_lat)
            ymax = grid_lat + (180 / pi) * (ydiff / 6378137)
            ymin = grid_lat - (180 / pi) * (ydiff / 6378137)
            area = "POLYGON(({0} {1}, {0} {3}, {2} {3}, {2} {1}, {0} {1}))".format(
                xmin, ymin, xmax, ymax
            )
            #poly is converted to a geoseries
            area_shply = shapely.wkt.loads(area)
            area_geos = gpd.GeoSeries(area_shply)
            box = area_geos.total_bounds
            #edge length of individual hexagon is calculated using the area
            edge = math.sqrt(Area**2 / (3 / 2 * math.sqrt(3)))
            #grid is created that has the central points of each hexagon
            hex_centers = create_hexgrid(box, edge)
            #Empty list that will contain the hexagon geometry
            hexagons = []
            #centre points are iterated through the function that creates a
            #hexagon around each of them and adds it to the list
            for center in hex_centers:
                hexagons.append(create_hexagon(edge, center[0], center[1]))
            #Geometry list is turned into a geodataframe
            planning_unit_grid = gpd.GeoDataFrame(geometry=hexagons, crs=crs)
            # unique PUID is assigned to each hexagon
            planning_unit_grid.name = "Planning Unit Grid"
            planning_unit_grid["PUID"] = planning_unit_grid.index + 1
            #file is saved for user to reuse
            # planning_unit_grid.to_file("planning_unit_grid.shp")
            break

        # 9 Return to Main Menu
        elif selection == 9:
            break
        else:
            print_warning_msg(msg_value_error)
            continue
    return planning_unit_grid


# %% Select planning units

# def select_planning_units(planning_unit_grid: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
#     """
#     Author: Ethan

#     Parameters
#     ----------
#     planning_unit_grid : gpd.GeoDataFrame
#         DESCRIPTION.

#     Returns
#     -------
#     TYPE
#         DESCRIPTION.

#     """

#     filtered_planning_unit_grid = planning_unit_grid.copy(deep=True)

#     if planning_unit_grid.empty:
#         print_warning_msg("No planning unit grid loaded.")
#         return planning_unit_grid

#     while True:
#         try:
#             selection = int(
#                 input(
#                     """
#     Select Planning Units
#         1 Manual Input
#         2 Interactive
#         3 Extents from File
#         9 Return to Main Menu
#     >>> """
#                 )
#             )
#         except ValueError:
#             print_warning_msg(msg_value_error)

#         if selection == 1:
#             # 1 Manual Input
#             while True:
#                 try:
#                     selection = int(
#                         input(
#                             """
#     Select Planning Units Manual Input Menu
#         1 Extents
#         2 PUIDS
#         3 Extents from File
#         9 Return to Select Planning Units Menu
#     >>> """
#                         )
#                     )
#                 except ValueError:
#                     print_warning_msg(msg_value_error)

#                 if selection == 1:
#                     # 1 Extents
#                     extent_str = input("Enter extents as xmin ymin xmax ymax: ")
#                     extent = list(map(float, extent_str.split()))

#                     poly = gpd.GeoSeries([{
#                         'type': 'Polygon',
#                         'coordinates': [[
#                             [extent[0], extent[1]],
#                             [extent[2], extent[1]],
#                             [extent[2], extent[3]],
#                             [extent[0], extent[3]],
#                             [extent[0], extent[1]]
#                         ]]
#                     }], crs='epsg:4326')
#                     selected_hexagons = filtered_planning_unit_grid[hexagons.intersects(poly[0])]
#                     break
#                 elif selection == 2:
#                     # 2 PUIDS
#                     userPUID = input("What is the PUID? Type the PUID's and put a space between each one':")
#                     selected_hexagons = hexagons[hexagons.PUID.isin(puids.split(','))]
#                     break
#                 elif selection == 3:
#                     # 3 Extents from File
#                     userShapefile = input("What is the path to the Shapefile?:")
#                     # Find intersecting hexagons
#                     selected_poly = gpd.read_file(userShapefile)
#                     selected_hexagons = hexagons[hexagons.intersects(selected_poly.geometry.unary_union)]
#                     break

#                 elif selection == 9:
#                     # 9 Return to Main Menu
#                     break
#                 else:
#                     print_warning_msg(msg_value_error)
#                     continue

#         elif selection == 2:
#             # 2 Interactive
#             continue
#         elif selection == 3:
#             # 3 Grid from File
#             continue
#         elif selection == 9:
#             # 9 Return to Main Menu
#             break
#         else:
#             print_warning_msg(msg_value_error)
#             continue

#     return filtered_planning_unit_grid


# %% Load conservation feature layers from file
def load_convservation_layers(conserv_layers: list) -> list[gpd.GeoDataFrame]:
    """
    Author: Nata

    Takes user selection to load planning/ conservation layers of interest

    Parameters
    ----------
    conserv_layers : list
        Takes a list of planning layers to load.

    Returns
    -------
    conserv_layers : list[gpd.GeoDataFrame]
        returns a geodataframe of the selected planning layers.

    """
    # get list of files to load
    while True:
        try:
            selection = int(
                input(
                    """
    Load Planning Layers
        1 Select Files
        2 All from Directory
        9 Return to Main Menu
    >>> """
                )
            )
        except ValueError:
            print_warning_msg(msg_value_error)
            continue

        # 1 Select Files
        if selection == 1:
            files = get_files(title="Select planning layer files")
            if files:
                conserv_layers = load_files(files, verbose)
            else:
                print_warning_msg("No files loaded from directory, please verify files and try again.")
                continue
            break

        # 2 All from Directory
        elif selection == 2:
            files = get_files_from_dir()
            if files:
                conserv_layers = load_files(files, verbose)
            else:
                print_warning_msg("No files loaded from directory, try selecting files manually.")
                continue
            break

        # 9 Return to Main Menu
        elif selection == 9:
            break
        else:
            print_warning_msg(msg_value_error)
            continue
    # TODO - add projection to target CRS once target CRS is setup properly
    # projected_layers = []
    # for layer in conserv_layers:
    #     projected_layers.append(layer.to_crs(target_crs))
    return conserv_layers


# %% Filter for specific conservation features
def query_conservation_layers(
    conserv_layers: list[gpd.GeoDataFrame],
) -> list[gpd.GeoDataFrame]:
    """
    Author: Nata

    Takes planning layers and user input on conservation features of interest to select by attribute and save new file

    Parameters
    ----------
    conserv_layers : list[gpd.GeoDataFrame]
        Takes the pre-loaded planning layers file.

    Returns
    -------
    TYPE
        Returns a geodataframe of only the selected conservation features.

    """

    if not len(conserv_layers):
        print_warning_msg("No planning layers loaded.")
        return []

    # This will reset the list of layers to the original loaded layers every time
    filtered_conserv_layers = []
    for layer in conserv_layers:
        filtered_conserv_layers.append(layer.copy(deep=True))
    for i in range(len(conserv_layers)):
        filtered_conserv_layers[i].name = conserv_layers[i].name

    attribute = ""

    def filter_by_attribute(conserv_layers: list[gpd.GeoDataFrame], attribute: any) -> list[gpd.GeoDataFrame]:
        filter = []
        for gdf in conserv_layers:
            for attr in gdf[attribute].unique():
                filter.append(attr)

        chosenFeatures = get_user_selection(filter, multi=True, title="Select features to keep")

        filtered_gdf_list = []
        for gdf in conserv_layers:
            if attribute in gdf.columns:
                filtered_gdf = gdf[gdf[attribute].astype(str).isin(chosenFeatures)]
                filtered_gdf.name = gdf.name
                filtered_gdf_list.append(filtered_gdf)
            else:
                print_warning_msg(f"Attribute {attribute} not found in {gdf.name}")
        return filtered_gdf_list

    while True:
        try:
            selection = int(
                input(
                    """
    Query Planning Layers
        1 ID
        2 CLASS_TYPE
        3 GROUP_
        4 NAME
        5 Choose Attribute
        9 Return to Main Menu
    >>> """
                )
            )
        # 5 By Area --> Not sure about this one, could produce another menu
        # to get extents from intput, file, or interactive on map, but that
        # may be redundant if we just limits to the bounds of the selected
        # planning units to start with.

        except ValueError:
            print_warning_msg(msg_value_error)
            continue

        # 1 ID
        if selection == 1:
            attribute = ID
            break
        # 2 CLASS_TYPE
        elif selection == 2:
            attribute = CLASS
            break
        # 3 GROUP_
        elif selection == 3:
            attribute = GROUP
            break
        # 4 NAME
        elif selection == 4:
            attribute = NAME
            break
        elif selection == 5:
            column_names = []
            for gdf in conserv_layers:
                column_names.extend(list(gdf.columns))
            column_names = list(set(column_names))
            sel = get_user_selection(column_names, title="Select attribute to filter by")
            attribute = sel[0] if sel else ""
            break
        # 9 Return to Main Menu
        elif selection == 9:
            break
        else:
            print_warning_msg(msg_value_error)
            continue

    if attribute:
        filtered_conserv_layers = filter_by_attribute(conserv_layers, attribute)

    return filtered_conserv_layers


# %% Calculate planning unit / conservation feature overlap
def calculate(planning_grid: gpd.GeoDataFrame, cons_layers: list[gpd.GeoDataFrame]) -> list[gpd.GeoDataFrame]:
    """Target function for processor pool. Intersects planning grid with each conservation layer
    and calculates area of overlap.
    Author: Mitch Albert

    :param planning_grid: The planning grid to intersect with the conservation layers.
    :type planning_grid: gpd.GeoDataFrame
    :param cons_layers: The conservation layers to intersect with the planning grid.
    :type cons_layers: list[gpd.GeoDataFrame]
    :return: The list of conservation layers after being intersected with the planning grid
             with an additional column containing the area of overlap.
    :rtype: list[gpd.GeoDataFrame]
    """
    intersections = []
    for layer in cons_layers:
        if not layer.empty:
            clipped_grid = gpd.clip(planning_grid, layer.geometry.convex_hull)  # this may not improve performance
            intersection = gpd.overlay(clipped_grid, layer, how="intersection")
            intersection[AMOUNT] = intersection.area
            intersection[AMOUNT] = intersection[AMOUNT].round().astype(int)
            intersections.append(intersection)
        else:
            print_warning_msg("Skipping empty conservation layer.")
    return intersections


def calculate_overlap(planning_grid: gpd.GeoDataFrame, cons_layers: list[gpd.GeoDataFrame]) -> list[gpd.GeoDataFrame]:
    """Intersect the planning grid with the conservation layers and calculate the area of overlap.
    Author: Mitch Albert

    :param planning_grid: The planning grid to intersect with conservation layers.
    :type planning_grid: gpd.GeoDataFrame
    :param cons_layers: A list of conservation layers that should contain only the desired
                        conservation features to intersect with the planning grid.
    :type cons_layers: list[gpd.GeoDataFrame]
    :return: The intersected gdfs, or an empty list if planning grid or conservation layers are not loaded,
             or if there are no intersecting features. The list will contain CORES * len(cons_layers) gdfs
    :rtype: list[gpd.GeoDataFrame]
    """

    # TODO: check if planning grid and conservation layer are in same CRS

    # check if planning grid and conservation layers are loaded, otherwise return empty list
    if not len(cons_layers):
        print_warning_msg("No conservation feature layers loaded.")
        return []
    if planning_grid.empty:
        print_warning_msg("No planning unit grid loaded.")
        return []

    # split planning grid into chunks to be processed by each core
    planning_grid_divisions = np.array_split(planning_grid, CORES)

    # define partial function to pass to pool, this enables passing multiple arguments to calculate() from the pool
    # otherwise we would have to pass a tuple of arguments
    calc_overlap_partial = partial(calculate, cons_layers=cons_layers)

    # this will hold the results of the pool
    intersections = []

    if verbose:
        print_info(f"Starting intersection calculations with {CORES} cores")
        progress = print_progress_start("Calculating intersections", dots=10, time=1)
    # start timer
    start_time = time()
    # Create a Pool object with the number of cores specified in CORES
    with Pool(CORES) as pool:
        # Iterate through the planning_grid_divisions and apply the calc_overlap_partial function to each element
        for result in pool.imap_unordered(calc_overlap_partial, planning_grid_divisions):
            intersections.extend(result)

    if verbose:
        print_progress_stop(progress)
        print_info_complete(f"Intersection calculations completed in: {(time() - start_time):.2f} seconds")

    return intersections


# %% CRS helper function
def validate_crs(crs: any, target_crs: str) -> bool:
    """
    Author: Winna
    Utility function to validate a Coordinate Reference System (CRS) and either correct it or inform users of the mismatch.

    Parameters:
    -----------
    crs : any
        The CRS to be validated. This can be in any format, such as a string or a dictionary.
    target_crs : str
        The target CRS that the input CRS should match.

    Returns:
    --------
    bool
        Returns True if the input CRS matches the target CRS, False otherwise.
    """
    if isinstance(crs, str):
        # If crs is a string, check if it matches the target CRS
        if crs == target_crs:
            return True
        else:
            # If it doesn't match, prompt the user to either correct it or fail
            user_input = input(
                f"The CRS '{crs}' does not match the target CRS '{target_crs}'. Would you like to correct it? [y/n]: "
            )
            if user_input.lower() == "y":
                # If the user wants to correct it, prompt for the correct CRS and check if it matches the target CRS
                corrected_crs = input("Enter the corrected CRS: ")
                if corrected_crs == target_crs:
                    return True
                else:
                    print(
                        f"The corrected CRS '{corrected_crs}' does not match the target CRS '{target_crs}'. Validation failed."
                    )
                    return False
            else:
                # If the user doesn't want to correct it, fail the validation
                print("Validation failed.")
                return False
    elif isinstance(crs, dict):
        # If crs is a dictionary, check if it has a 'crs' key and if its value matches the target CRS
        if "crs" in crs:
            if crs["crs"] == target_crs:
                return True
            else:
                # If it doesn't match, prompt the user to either correct it or fail
                user_input = input(
                    f"The CRS '{crs['crs']}' does not match the target CRS '{target_crs}'. Would you like to correct it? [y/n]: "
                )
                if user_input.lower() == "y":
                    # If the user wants to correct it, prompt for the correct CRS and check if it matches the target CRS
                    corrected_crs = input("Enter the corrected CRS: ")
                    if corrected_crs == target_crs:
                        crs["crs"] = corrected_crs
                        return True
                    else:
                        print(
                            f"The corrected CRS '{corrected_crs}' does not match the target CRS '{target_crs}'. Validation failed."
                        )
                        return False
                else:
                    # If the user doesn't want to correct it, fail the validation
                    print("Validation failed.")
                    return False
        else:
            # If the dictionary doesn't have a 'crs' key, prompt the user to either correct it or fail
            user_input = input(
                "The input dictionary does not have a 'crs' key. Would you like to add it and enter a CRS? [y/n]: "
            )
            if user_input.lower() == "y":
                # If the user wants to add a 'crs' key, prompt for the CRS and check if it matches the target CRS
                corrected_crs = input("Enter the CRS: ")
                if corrected_crs == target_crs:
                    crs["crs"] = corrected_crs
                    return True
                else:
                    print(
                        f"The entered CRS '{corrected_crs}' does not match the target CRS '{target_crs}'. Validation failed."
                    )


# %% Plotting function
def plot_layers(
    planning_unit_grid: gpd.GeoDataFrame,
    conserv_layers: list[gpd.GeoDataFrame],
    filtered_conserv_layers: list[gpd.GeoDataFrame],
):
    """Display the view layers menu and allow the user to select which layers to plot.
    Author: Mitch Albert

    :param planning_unit_grid: The planning unit grid.
    :type planning_unit_grid: gpd.GeoDataFrame
    :param conserv_layers: The conservation feature layers without filtering.
    :type conserv_layers: list[gpd.GeoDataFrame]
    :param filtered_conserv_layers: The selected conservation features after filtering.
    :type filtered_conserv_layers: list[gpd.GeoDataFrame]
    """

    def plot(layers: list[gpd.GeoDataFrame]):
        """Internal function to plot the layers. This is called by the view layers menu.
        Only acceps a list of geodataframes and loops through them plotting each one.
        Author: Mitch Albert

        :param layers: The list of gpd.geodataframes to plot.
        :type layers: list[gpd.GeoDataFrame]
        """
        if len(layers):
            try:
                if verbose:
                    progress = print_progress_start("Plotting", dots=3)
                for layer in layers:
                    if layer.empty:
                        print_warning_msg("Nothing to plot.")
                        continue
                    fig, ax = plt.subplots(figsize=(10, 10))
                    layer.plot(ax=ax)
                    if hasattr(layer, 'name'):
                        ax.set_title(layer.name)
                    plt.show()
            except Exception as e:
                print_warning_msg(f"Error while plotting\n")
                print(e)
            finally:
                if verbose:
                    print_progress_stop(progress)
        else:
            print_warning_msg("Nothing plot.")
        return

    while True:
        try:
            selection = int(
                input(
                    """
    View Layers Menu:
        1 Planning Unit Grid
        2 Conservation Features Files
        3 Filtered Conservation Features
        9 Return to Main Menu
    >>> """
                )
            )
        except ValueError:
            print_warning_msg(msg_value_error)
            continue

        # 1 Planning Unit Grid
        if selection == 1:
            print_info("Plotting Planning Unit Grid...")
            plot([] if planning_unit_grid.empty else [planning_unit_grid])
            continue

        # 2 All Conservation Features Files
        elif selection == 2:
            print_info("Plotting Conservation Features...")
            plot(conserv_layers)
            continue

        # 3 Filtered Conservation Features
        elif selection == 3:
            print_info("Plotting Filtered Conservation Features...")
            plot(filtered_conserv_layers)
            continue

        # 9 Return to Main Menu
        elif selection == 9:
            break

        else:
            print_warning_msg(msg_value_error)
            continue
    return


# %% Main
def main():
    """Main function. Calls main_menu() which will runs until user enters 9 to exit
    Author: Mitch Albert
    """

    def main_menu():
        """Print main menu and return user selection. If user selection is not
        valid, will print error message and return to main menu. If user
        enters 9, the program will exit. Otherwise calls appropriate function based
        on user selection.
        Author: Mitch Albert
        """
        # intialize variables
        work_saved = False  # flag to save the results
        planning_unit_grid = gpd.GeoDataFrame()  # planning unit grid
        filtered_planning_unit_grid = gpd.GeoDataFrame()  # this is the planning unit grid after filtering, now obsolete
        conserv_layers = []  # list of planning layers gdfs, name will change to conservation_features
        filtered_conserv_layers = []  # this is list of conservation_features gdfs after filtering
        intersections_gdf = []  # list of gdfs of planning unit / conservation feature intersections
        intersections_df = (
            pd.DataFrame()
        )  # dataframe of planning unit / conservation feature intersections, used to easy csv export

        # target_crs = get_crs()

        while True:
            try:
                selection = int(
                    input(
                        """
    Main Menu:
        1 Create Planning Unit Grid
        2 Select Planning Units
        3 Load Conservation Features Files
        4 Select Conservation Features
        5 View Layers
        6 Calculate Overlap
        7 Save Results
        9 Quit
    >>> """
                    )
                )
            except ValueError:
                print_warning_msg(msg_value_error)
                continue

            # 1 Create Planning Unit GridFeatures
            if selection == 1:
                planning_unit_grid = create_planning_unit_grid()
                continue

            # 2 Select Planning Units
            elif selection == 2:
                # NOTE: this is now obsolete, but only commenting out for now
                # filtered_planning_unit_grid = select_planning_units(planning_unit_grid)
                continue

            # 3 Load Conservation Features Files
            elif selection == 3:
                conserv_layers = load_convservation_layers(conserv_layers)
                for layer in conserv_layers:
                    filtered_conserv_layers.append(layer.copy(deep=True))
                for i in range(len(conserv_layers)):
                    filtered_conserv_layers[i].name = conserv_layers[i].name
                continue

            # 4 Select conservation features
            elif selection == 4:
                filtered_conserv_layers = query_conservation_layers(conserv_layers)
                continue

            # 5 View Layers
            elif selection == 5:
                plot_layers(planning_unit_grid, conserv_layers, filtered_conserv_layers)
                continue

            # 6 Calculate Overlap
            elif selection == 6:
                # TODO: update to remove filtered_planning_unit_grid
                # intersections_gdf = calc_overlap(
                #     filtered_planning_unit_grid, filtered_conserv_layers
                # )
                intersections_gdf = calculate_overlap(planning_unit_grid, filtered_conserv_layers)

                if len(intersections_gdf):
                    intersections_df = pd.DataFrame(gpd.GeoDataFrame(pd.concat(intersections_gdf, ignore_index=True)))
                # intersections_df.sort_values(PUID, ascending=True, inplace=True)
                continue

            # 7 Save Results
            elif selection == 7:
                if not planning_unit_grid.empty:
                    save_gdf(planning_unit_grid)
                else:
                    print_warning_msg("No planning unit grid to save.")

                save_filtered_conserv_layers = False
                for gdf in filtered_conserv_layers:
                    if not gdf.empty:
                        save_gdf(gdf)
                        save_filtered_conserv_layers = True
                    else:
                        print_warning_msg("Skipping saving empty conservation feature layer.")
                if not save_filtered_conserv_layers:
                    print_warning_msg("No conservation feature layers to save.")

                if intersections_df.empty:
                    print_warning_msg("No intersection results to save.")
                else:
                    file_name = get_save_file_name(title="Save results to csv", f_types=ft_csv)
                    # Columns names / order need to be updated to match sample file from client, waiting to receive
                    intersections_df.to_csv(
                        file_name,
                        header=[SPECIES, PU, AMOUNT],
                        columns=[ID, PUID, AMOUNT],
                        index=False,
                    )
                    work_saved = True
                continue

            # 9 Quit
            elif selection == 9:
                quit = 'y'
                if not work_saved:
                    print_warning_msg("No overlap results were saved.")
                    quit = input("Are you sure you want to quit? (y/n): ").casefold()
                if quit == "y":
                    break
                continue
            else:
                print_warning_msg(msg_value_error)
            continue
        return

    main_menu()

    print_info_complete("All done!")

    return


if __name__ == "__main__":
    if run_tests:
        input("\nTESTING COMPLETE")
    else:
        main()

# %%
