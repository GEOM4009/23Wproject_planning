# -*- coding: utf-8 -*-
"""
planning.py
Authors: Mitch, Lucas, Ethan, Nata, Winaa

This file contains the main script for the GEOM4009 planning project.
It contains the main menu and all the functions for the different the
different steps of the data and planning process.

NOTE: This script has its own environment availble to build with the
      planningproj_env.yml file.
      It can also be run in the geom4009 environment, but will require
      the installation of the following additional packages:

        conda install -c conda-forge tk  --> provides the tkinter GUI

"""
# Import modules
from util import *
import os

os.environ["USE_PYGEOS"] = "0"
from time import time

from shapely.geometry import Point, Polygon
from shapely import wkt
from math import cos, sin, sqrt, radians, ceil

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

from multiprocessing import Pool

import numpy as np
import psutil
from functools import partial

# Global Variables
verbose = True
CORES = psutil.cpu_count(logical=False)
target_crs = TARGET_CRS
intro = True

# %% Obtain the CRS from the user


def get_crs():
    """
    Author: Ethan
    The user enters the crs that will be used for the all of the geoDataFrames.
    This will keep a consistent and projected CRS, which is required for the overlay
    operations to work correctly. Note that the crs may be overridden if the user
    loads a pre-existing planning unit grid with a projected CRS, this is because the
    crs of the planning unit grid will be used instead to avoid distortion.

    """

    global target_crs
    title = bu("Enter a CRS to project all files to:")
    while True:
        # Ask user for CRS
        crs = input(
            f"""
    {title}
       [1] Canada Albers Equal Area
        2  Extract from file
        -  Any EPSG number (4087)
        -  Any Valid CRS string (e.g. 'EPSG:4087')
        9  Quit
    >>> """
        )

        # Try to cast to an int
        try:

            if crs == DEFAULT_INPUT:
                crs = DEFAULT_CRS_INPUT
                print(f"\t{crs}")

            crs = int(crs)

            # Create CRS for Albers Equal Area
            if crs == 1:
                crs = TARGET_CRS

            # extract the crs from the file
            elif crs == 2:
                file = get_file(title="Select a file to extract the CRS from")
                if not file:
                    continue
                gdf = load_files(file)
                if not gdf.crs:
                    print_warning_msg("No CRS found in file. Please try again.")
                    continue
                crs = gdf.crs

            # Quit
            elif crs == 9:
                print_info("Quitting...")
                exit(0)

            # If an EPSG number
            else:
                crs = "EPSG:" + str(crs)
        except ValueError:
            # This is fine, we will just try the string as the CRS
            pass
        # Try to create the CRS
        try:
            gdf = gpd.GeoDataFrame(geometry=[Point(0, 0)], crs=crs)
            if not gdf.crs.is_projected:
                print_warning_msg("CRS is not projected. Please try again.")
                continue
            else:
                target_crs = crs
                print_info(f"CRS set to: {gdf.crs.to_string()}")

        except Exception as e:
            print_warning_msg("Invalid CRS. Please try again.")
            continue
        break

    return


def get_area_input() -> float:
    """Parse user input for grid cell area.
    Prompt user until valid input is received or quit is selected.
    Usage: <number><suffix> (ex. 25km)
    Suffixes: m , hm, ha, km (case insensitive)
    Author: Mitch Albert

    :return: Area in square meters
    :rtype: float
    """

    while True:
        input_str = input(f"Hexagonal Cell Area in {M_SQ}, {HM_SQ}, or {KM_SQ}, enter in format <number><suffix> (ex. 25km): ")

        if input_str.startswith('-'):
            print_warning_msg("Area cannot be negative")
            continue

        # Remove spaces
        input_str = input_str.replace(" ", "")

        # initialize empty strings
        num_str = ""
        suffix_str = ""

        # parse the input until we hit a non-digit or '.' character
        for i, char in enumerate(input_str):
            if char.isdigit() or char == ".":
                num_str += char
            else:
                suffix_str = (input_str[i:])[:2]
                break

        # try to convert the digit porttion to a float
        try:
            area = float(num_str)
        except Exception:
            print_warning_msg(f"Unable to parse input from string: '{input_str}', usage: <number><suffix> (ex. 250km)")
            continue

        # find a key in the suffix dictionary that starts with the suffix string
        for key in SUFFIX_DICT.keys():
            if key.startswith(suffix_str):
                suffix_str = key
        if suffix_str not in SUFFIX_DICT:
            print_warning_msg(f"Unable to detect units, defaulting to {DEFAULT_UNITS_SQ} ({DEF_UNITS_SQ})")
            suffix_str = DEF_UNITS_SQ
        break

    print_info(f"Area: {area}, Units: {suffix_str}")

    return (area * SUFFIX_DICT[suffix_str]**2, suffix_str)


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
    c = [[x + cos(radians(angle)) * l, y + sin(radians(angle)) * l] for angle in range(0, 360, 60)]
    return Polygon(c)


def create_hexgrid(bbx, area):
    """
    Author:Kadir Şahbaz
    returns an array of Points describing hexagons centers that are inside the given bounding_box
    :param bbx: The containing bounding box. The bbox coordinate should be in Webmercator.
    :param side: The size of the hexagons'
    :return: The hexagon grid
    Source:https://gis.stackexchange.com/questions/341218/creating-a-hexagonal-grid-of-regular-hexagons-of-definite-area-anywhere-on-the-g
    """
    side = sqrt(area / (1.5 * sqrt(3)))

    grid = []
    v_step = sqrt(3) * side
    h_step = 1.5 * side

    x_min = min(bbx[0], bbx[2])
    x_max = max(bbx[0], bbx[2])
    y_min = min(bbx[1], bbx[3])
    y_max = max(bbx[1], bbx[3])

    h_skip = ceil(x_min / h_step) - 1
    h_start = h_skip * h_step

    v_skip = ceil(y_min / v_step) - 1
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

    return (grid, side)


def create_planning_unit_grid() -> gpd.GeoDataFrame:
    """
    Author: Lucas McPhail
    Take user input to create a hexagonal planning
    grid that is defined by a central coordinate, cell resolution,
    and grid height and width.
    It can also create this grid using other methods, such as taking a
    shapefile as input, the CRS and the bounds of that file will be
    determined and used to create the planning grid.
    Parameters
    ----------
    Area: float
        Size of grid cell that the user will use, the units will be
        the same units as the CRS that the user specifies
    grid_size_x: float
        width of the grid
    grid_size_y: float
        height of the grid
    grid_x_coor: float
        y coordinate for center of grid
    grid_y_coor: float
        y coordinate for center of grid
    Returns
    -------
    planning_unit_grid: gpd.GeoDataFrame
        hexagon grid shapefile that matches the dimensions specified by the user

    """

    planning_unit_grid = gpd.GeoDataFrame()
    global target_crs
    title = bu("Create Planning Unit Grid:")

    while True:
        selection = (
            input(
                f"""
    {title}
       [1] Create Grid from Shape File extents
        2  Create Grid from Shape File extents and clip to shape
        3  Load existing Grid from File
        4  Create Grid from User Input
        9  Return to Main Menu
    >>> """
            )
        )

        if selection == DEFAULT_INPUT:
            selection = DEFAULT_GRID_INPUT
            print(f"\t{selection}")

        try:
            selection = int(selection)
        except ValueError:
            print_warning_msg(msg_value_error)
            continue

        # 1 Create Grid from Shape File extents
        if selection == 1 or selection == 2:
            # user can enter the file that will define the bounds and cell area
            file = get_file(title="Select a file to load the extents from")
            if not file:
                continue
            file = load_files(file, verbose)

            area, suf = get_area_input()
            print (area, suf)
            file.to_crs(crs=target_crs, inplace=True)
            box = file.total_bounds
            # edge length of individual hexagon is calculated using the area
            # edge = math.sqrt(Area**2 / (3 / 2 * math.sqrt(3)))

            try:
                if verbose:
                    progress = print_progress_start(ABORT + "Generating Planning Unit Grid")

                hex_centers, edge = create_hexgrid(box, area)
                # Empty list is created that will contain the hexagons
                hexagons = []
                # centre points are iterated through the function that creates a
                # hexagon around each of them and adds it to the list
                for center in hex_centers:
                    hexagons.append(create_hexagon(edge, center[0], center[1]))
                # Geometry list is turned into a geodataframe
                planning_unit_grid = gpd.GeoDataFrame(geometry=hexagons, crs=target_crs)
                planning_unit_grid.to_crs(crs=target_crs, inplace=True)
                # unique PUID is assigned to each hexagon
                planning_unit_grid[PUID] = planning_unit_grid.index + 1

                clipped = ''
                # Clip the hexagons to the shape of the input shapefile
                if selection == 2:
                    hex_gdf_clipped = gpd.clip(planning_unit_grid, file)
                    # Filter the original GeoDataFrame to only include the hexagons within the clipped area
                    hex_ids = set(hex_gdf_clipped[PUID])
                    planning_unit_grid = planning_unit_grid[planning_unit_grid[PUID].isin(hex_ids)]
                    planning_unit_grid.reset_index(drop=True, inplace=True)
                    planning_unit_grid[PUID] = planning_unit_grid.index + 1
                    clipped = '_clipped'

                planning_unit_grid.name = f'Planning_Unit_Grid_{str(area/(SUFFIX_DICT[suf]**2)).replace(".","-")}{suf.replace(SQ,"2")}{clipped}'
                # planning_unit_grid.to_file("planning_unit_grid.shp")

            except KeyboardInterrupt:
                print_warning_msg(f"Grid Generation Aborted\n)")
            except Exception as e:
                print_warning_msg(f"Error during Grid Generation\n")
                print(e)
            finally:
                if verbose:
                    print_progress_stop(progress)
            break

        # 3 Load existing Grid from File
        elif selection == 3:
            file = get_file(title="Select a file to load the grid from")
            if file:
                planning_unit_grid = load_files(file, verbose)
                if not planning_unit_grid.crs.is_projected:
                    print_warning_msg("Loaded grid is not in a projected CRS, porjecting to selected CRS instead, this may cause distortion!")
                    planning_unit_grid = project_gdfs([planning_unit_grid], target_crs)[0]
                else:
                    target_crs = planning_unit_grid.crs
                    print_warning_msg(f"Loaded grid will override target CRS.")
                    print_info(f"CRS is now set to {target_crs.to_string()}.")
                if verbose:
                    print_info(f"Hex area: {round(planning_unit_grid.geometry.area[0])}")
            else:
                print_warning_msg("No file loaded, please try again.")
                continue

            break

        # 4 Create Grid from User Input
        elif selection == 4:
            # The inputs below will get the information needed to
            # create a boundary that will be filled with the hexagons as
            # well as define the hexagon cell size
            area, suf = get_area_input()
            grid_size_x = get_user_float(f'Overall Size of Grid in X ({suf.replace(SQ,"")}): ') * SUFFIX_DICT[suf]
            grid_size_y = get_user_float(f'Overall Size of Grid in Y ({suf.replace(SQ,"")}): ') * SUFFIX_DICT[suf]
            grid_x_coor = get_user_float("Central x coordinate of grid (Same units as CRS): ")
            grid_y_coor = get_user_float("Central y coordinate of grid (Same units as CRS): ")

            if verbose:
                progress = print_progress_start(ABORT + "Generating Planning Unit Grid")
            try:
                # Half of the grid width and height can be added to the central
                # coordinate to create a study area that meets the criteria
                xdiff = grid_size_x / 2
                ydiff = grid_size_y / 2
                # Bounds of the area of interest are created by adding the half the
                # grid size to each coordinate
                xmax = grid_x_coor + xdiff
                xmin = grid_x_coor - xdiff
                ymax = grid_y_coor + ydiff
                ymin = grid_y_coor - ydiff
                box = "POLYGON(({0} {1}, {0} {3}, {2} {3}, {2} {1}, {0} {1}))".format(xmin, ymin, xmax, ymax)
                # poly is converted to a geoseries
                area_shply = wkt.loads(box)
                area_geos = gpd.GeoSeries(area_shply)
                box = area_geos.total_bounds
                # edge length of individual hexagon is calculated using the area
                # edge = math.sqrt(Area**2 / (3 / 2 * math.sqrt(3)))
                # grid is created that has the central points of each hexagon
                hex_centers, edge = create_hexgrid(box, area)
                # Empty list that will contain the hexagon geometry
                hexagons = []
                # centre points are iterated through the function that creates a
                # hexagon around each of them and adds it to the list
                for center in hex_centers:
                    hexagons.append(create_hexagon(edge, center[0], center[1]))


                # Geometry list is turned into a geodataframe
                planning_unit_grid = gpd.GeoDataFrame(geometry=hexagons, crs=target_crs)
                # unique PUID is assigned to each hexagon
                planning_unit_grid.name = f'Planning_Unit_Grid_{str(area/(SUFFIX_DICT[suf]**2)).replace(".","-")}{suf.replace(SQ,"2")}'
                planning_unit_grid[PUID] = planning_unit_grid.index + 1
                # file is saved for user to reuse
                # planning_unit_grid.to_file("planning_unit_grid.shp")
            except KeyboardInterrupt:
                print_warning_msg(f"Grid Generation Aborted\n)")
            except Exception as e:
                print_warning_msg(f"Error during Grid Generation\n")
                print(e)
            finally:
                if verbose:
                    print_progress_stop(progress)
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
def load_convservation_layers() -> list[gpd.GeoDataFrame]:
    """
    Author: Nata

    Takes user selection to load planning/ conservation layers of interest

    Returns
    -------
    conserv_layers : list[gpd.GeoDataFrame]
        returns a geodataframe of the selected conservation feature layers.

    """
    conserv_layers = [] # list to hold conservation feature layers
    title = bu("Load Conservation Feature Layers:")
    # get list of files to load
    while True:
        selection = (
            input(
                f"""
    {title}
       [1] Select Files
        2  All from Directory
        9  Return to Main Menu
    >>> """
            )
        )

        if selection == DEFAULT_INPUT:
            selection = DEFAULT_LOAD_CONSERVATION_INPUT
            print(f"\t{selection}")
        try:
            selection = int(selection)
        except ValueError:
            print_warning_msg(msg_value_error)
            continue


        # 1 Select Files
        if selection == 1:
            files = get_files(title="Select Conservation Feature files")
            if files:
                conserv_layers = load_files(files, verbose)
            else:
                print_warning_msg("No files loaded, please verify files and try again.")
                continue
            break

        # 2 All from Directory
        elif selection == 2:
            files = get_files_from_dir([ft_shapefile, ft_geo_package])
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

    projected_layers = project_gdfs(conserv_layers, target_crs)

    return projected_layers


# %% Filter for specific conservation features
def query_conservation_layers(
    conserv_layers: list[gpd.GeoDataFrame],
) -> list[gpd.GeoDataFrame]:
    """
    Author: Nata

    Takes conservation feature layers and user input on conservation features of interest to select by attribute and save new file

    Parameters
    ----------
    conserv_layers : list[gpd.GeoDataFrame]
        The pre-loaded conservation feature layers files.

    Returns
    -------
    TYPE
        Returns a geodataframe of only the selected conservation features.

    """

    if not len(conserv_layers):
        print_warning_msg("No conservation feature layers loaded.")
        return []

    # This will reset the list of layers to the original loaded layers every time
    filtered_conserv_layers = []
    for layer in conserv_layers:
        filtered_conserv_layers.append(layer.copy(deep=True))
    for i in range(len(conserv_layers)):
        filtered_conserv_layers[i].name = "".join(conserv_layers[i].name.split(".")[:-1])+"_filtered" if hasattr(conserv_layers[i], "name") else f"filtered_{i}"

    attribute = ""

    def filter_by_attribute(conserv_layers: list[gpd.GeoDataFrame], attribute: any) -> list[gpd.GeoDataFrame]:
        filter = []
        for gdf in conserv_layers:
            if gdf.empty:
                continue
            if attribute in gdf.columns:
                filter.extend(gdf[attribute].unique())
        filter = list(set(filter))
        filter.sort()

        chosenFeatures = get_user_selection(filter, multi=True, title="Select features to keep")
        filtered_gdf_list = []
        if not chosenFeatures:
            print_warning_msg("No features selected.")
            filtered_gdf_list = conserv_layers
        else:
            for gdf in conserv_layers:
                if attribute in gdf.columns:
                    filtered_gdf = gdf[gdf[attribute].astype(str).isin(chosenFeatures)]
                    filtered_gdf.name = gdf.name if hasattr(gdf, "name") else ""
                    filtered_gdf_list.append(filtered_gdf)
                else:
                    print_warning_msg(f"Attribute {attribute} not found in gdf {gdf.name}")
        return filtered_gdf_list

    title = bu("Query Conservation Feature Layers:")
    while True:
        selection = (
            input(
               f"""
    {title}
       [1] ID
        2  CLASS_TYPE
        3  GROUP_
        4  NAME
        5  Choose Attribute
        9  Return to Main Menu
    >>> """
                )
            )

        if selection == DEFAULT_INPUT:
            selection = DEFAULT_QUEURY_INPUT
            print(f"\t{selection}")

        try:
            selection = int(selection)
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
            column_names.remove(GEOMETRY)
            column_names.sort()
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
        filtered_conserv_layers = filter_by_attribute(filtered_conserv_layers, attribute)

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
            clipped_grid = gpd.clip(planning_grid, layer.geometry.convex_hull)
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

    # sort the results by PUID, ID, and AMOUNT
    for i in range(len(intersections)):
        intersections[i] = intersections[i].sort_values([PUID, ID, AMOUNT])

    if verbose:
        print_progress_stop(progress)
        print_info_complete(f"Intersection calculations completed in: {(time() - start_time):.2f} seconds")

    # check if any results were found
    results = False
    for layer in intersections:
        if not layer.empty:
            results = True
            break
    if not results:
        print_warning_msg("No intersecting features found.")

    return intersections


# %% CRS helper function
def validate_crs(crs: any, target_crs: str) -> bool:
    """
    Author: Winaa
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
                    progress = print_progress_start(ABORT + "Plotting", dots=3)
                for layer in layers:
                    if layer.empty:
                        print_warning_msg("Nothing to plot.")
                        continue
                    # get the column name to colour plot if it exists
                    if MAP_COLUMN in list(layer.columns):
                        fig, ax = plt.subplots(1, 1, figsize=(10, 10))
                        layer.plot(column=MAP_COLUMN, ax=ax, categorical=True, legend=True)
                    else:
                        ax = layer.plot(figsize=(10, 10))
                    if hasattr(layer, "name"):
                        ax.set_title(layer.name)
                    plt.show()
            except KeyboardInterrupt:
                print_warning_msg(f"Plotting Aborted\n")
            except Exception as e:
                print_warning_msg(f"Error while plotting\n")
                print(e)
            finally:
                if verbose:
                    print_progress_stop(progress)
        else:
            print_warning_msg("Nothing plot.")
        return
    title = bu("View Layers Menu:")
    while True:
        selection = (
            input(
                f"""
    {title}
        1  Planning Unit Grid
        2  Conservation Features Files
        3  Filtered Conservation Features
       [9] Return to Main Menu
    >>> """
            )
        )
        if selection == DEFAULT_INPUT:
            selection = DEFAULT_PLOT_INPUT
            print(f"\t{selection}")
        try:
            selection = int(selection)
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


def project_gdfs(gdfs: list[gpd.GeoDataFrame], crs) -> list[gpd.GeoDataFrame]:
    projected_gdfs = []
    for gdf in gdfs:
        if gdf.crs != crs:
            name = gdf.name if hasattr(gdf, "name") else ""
            print_info(f"Projecting {name} to {crs}")
            projected_gdfs.append(gdf.to_crs(crs))
        else:
            projected_gdfs.append(gdf.copy(deep=True))
        if hasattr(gdf, "name"):
            projected_gdfs[-1].name = gdf.name
    return projected_gdfs


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
        # filtered_planning_unit_grid = gpd.GeoDataFrame()  # this is the planning unit grid after filtering, now obsolete
        conserv_layers = []  # list of conservation feature layers gdfs, name will change to conservation_features
        filtered_conserv_layers = []  # this is list of conservation_features gdfs after filtering
        intersections_gdf = []  # list of gdfs of planning unit / conservation feature intersections
        intersections_df = (
            pd.DataFrame()
        )  # dataframe of planning unit / conservation feature intersections, used to easy csv export


        if intro:
            print(intro_message)

        get_crs()
        title = bu("Main Menu:")
        while True:
            try:
                selection = int(
                    input(
                        f"""
    {title}
        1  Create Planning Unit Grid
        2  Load Conservation Features Files
        3  Filter Conservation Features
        4  View Layers
        5  Calculate Overlap
        6  Save Results
        9  Quit
    >>> """
                    )
                )
            except ValueError:
                print_warning_msg(msg_value_error)
                continue

            # 1 Create Planning Unit GridFeatures
            if selection == 1:
                planning_unit_grid = create_planning_unit_grid()
                if not planning_unit_grid.empty:
                    conserv_layers = project_gdfs(conserv_layers, planning_unit_grid.crs)
                    filtered_conserv_layers = project_gdfs(filtered_conserv_layers, planning_unit_grid.crs)
                continue

                # 2 Select Planning Units
                # elif selection == 2:
                # NOTE: this is now obsolete, but only commenting out for now
                # filtered_planning_unit_grid = select_planning_units(planning_unit_grid)
                continue

            # 2 Load Conservation Features Files
            elif selection == 2:
                conserv_layers = load_convservation_layers()
                for layer in conserv_layers:
                    filtered_conserv_layers.append(layer.copy(deep=True))
                for i in range(len(conserv_layers)):
                    filtered_conserv_layers[i].name = (
                        conserv_layers[i].name if hasattr(conserv_layers[i], "name") else ""
                    )
                continue

            # 3 Select conservation features
            elif selection == 3:
                filtered_conserv_layers = query_conservation_layers(conserv_layers)
                continue

            # 4 View Layers
            elif selection == 4:
                plot_layers(planning_unit_grid, conserv_layers, filtered_conserv_layers)
                continue

            # 5 Calculate Overlap
            elif selection == 5:
                work_saved = False
                intersections_gdf = calculate_overlap(planning_unit_grid, filtered_conserv_layers)
                if len(intersections_gdf):
                    intersections_df = pd.DataFrame(gpd.GeoDataFrame(pd.concat(intersections_gdf, ignore_index=True)))
                continue

            # 6 Save Results
            elif selection == 6:
                if not planning_unit_grid.empty:
                    initial_file = (
                        planning_unit_grid.name if hasattr(planning_unit_grid, "name") else "planning_unit_grid"
                    )
                    if not save_gdf(
                        planning_unit_grid,
                        title="Save planning unit grid to file",
                        initialfile=initial_file,
                        verbose=verbose,
                    ):
                        print_warning_msg("Planning unit grid not saved.")
                    # TODO: add check to see if planning unit grid was already from file
                    # if from file, then don't save planning unit grid unless it
                    # was projected to a different crs
                else:
                    print_warning_msg("No planning unit grid to save.")

                if len(filtered_conserv_layers):
                    for i in range(len(filtered_conserv_layers)):
                        if not filtered_conserv_layers[i].empty:
                            initial_file = (
                                filtered_conserv_layers[i].name
                                if hasattr(filtered_conserv_layers[i], "name")
                                else "conservation_layer" + str(i)
                            )
                            if not save_gdf(
                                filtered_conserv_layers[i],
                                title="Save filtered conservation feature layer to file",
                                initialfile=initial_file,
                                verbose=verbose,
                            ):
                                print_warning_msg("Conservation feature layer not saved.")
                        else:
                            print_warning_msg("Skipping saving empty conservation feature layer.")
                else:
                    print_warning_msg("No conservation feature layers to save.")

                if intersections_df.empty:
                    print_warning_msg("No intersection results to save.")
                else:
                    print_info(f"Saving results")
                    file_name = get_save_file_name(
                        title="Save results to csv", f_types=ft_csv, initialfile=DEFAULT_RESULTS_FILE_NAME
                    )
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
                quit = "y"
                if not work_saved:
                    print_warning_msg("No overlap results were saved.")
                    quit = input("Are you sure you want to quit? (y/[n]): ").lower()
                if quit == "":
                    quit = DEFAULT_QUIT
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
    main()

# %%
