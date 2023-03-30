# -*- coding: utf-8 -*-
"""
"""
# Import modules
from util import *
from defs import *
import argparse
import os

import threading
import app
from time import sleep

from shapely.geometry import Polygon
import shapely
from math import pi, cos, sqrt
import math


os.environ["USE_PYGEOS"] = "0"
import geopandas as gpd
import pandas as pd


# Global Variables
run_tests = False
verbose = True

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

def create_planning_unit_grid(planning_unit_grid) -> gpd.GeoDataFrame:
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
    planning_unit_grid : gpd.geodataframe
        if a previuos hexagonal grid has been created it can be input
        to skip the creation of a new grid
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
    Prj: float
        CRS the grid will be output with
    Returns
    -------
    TYPE
        Description

    """

    while True:
        try:
            selection = int(
                input(
                    """
    Create Planning Unit Grid
        1 Manual Input
        2 Interactive
        3 Grid from File
        4 Extents from File
        5 View on Map
        9 Return to Main Menu
    >>> """
                )
            )
        except ValueError:
            print_error_msg(msg_value_error)

        if selection == 1:
            # 1 Manual Input
            #The inputs below will get the information needed to
            #create a boundary that will be filled with the hexagons as
            #well as define the hexagon cell size
            Area = get_user_float("Grid Cell Area (Meters Squared):")
            grid_size_x = get_user_float("Grid Size X (m): ")
            grid_size_y = get_user_float("Grid Size Y (m): ")
            grid_lat = get_user_float("Latitude of grid anchor point (dd): ")
            grid_lon = get_user_float("Longitude of grid anchor point (dd): ")
            Prj = get_user_float("Enter CRS code: ")
            #Half of the grid width and height can be added to the central
            #coordinate to create a study area that meets the criteria
            xdiff = grid_size_x / 2
            ydiff = grid_size_y / 2

            xmax = grid_lon + (180 / pi) * (xdiff / 6378137) / cos(grid_lat)
            xmin = grid_lon - (180 / pi) * (xdiff / 6378137) / cos(grid_lat)
            ymax = grid_lat + (180 / pi) * (ydiff / 6378137)
            ymin = grid_lat - (180 / pi) * (ydiff / 6378137)
            area = "POLYGON(({0} {1}, {0} {3}, {2} {3}, {2} {1}, {0} {1}))".format(xmin, ymin, xmax, ymax)
            area_shply = shapely.wkt.loads(area)
            area_geos = gpd.GeoSeries(area_shply)
            box = area_geos.total_bounds
            edge = math.sqrt(Area**2/(3/2 * math.sqrt(3)))
            hex_centers = create_hexgrid(box, edge)
            hex_centers
            hexagons = []
            for center in hex_centers:
                hexagons.append(create_hexagon(edge, center[0], center[1]))
                
            planning_unit_grid = gpd.GeoDataFrame(geometry = hexagons, crs = Prj)
            #unique PUID is assigned to each hexagon
            planning_unit_grid["PUID"] = planning_unit_grid.index + 1
            planning_unit_grid.to_file("planning_unit_grid.shp")
            break
        elif selection == 2:
            # 2 Interactive
            print(app.get_input_from_map())
            continue
        elif selection == 3:
            # 3 Grid from File
            file = get_file(title="Select a file to load the grid from")
            print(file)
            planning_unit_grid = gpd.read_file(file)
            break
        elif selection == 4:
            # 4 Extents from File
            file = get_file(title="Select a file to load the extents from")
            Area = get_user_float("Grid Cell Area (Meters Squared):")
            Prj = file.crs
            box = file.total_bounds
            
            edge = math.sqrt(Area**2/(3/2 * math.sqrt(3)))
            hex_centers = create_hexgrid(box, edge)
            hex_centers
            hexagons = []
            for center in hex_centers:
                hexagons.append(create_hexagon(edge, center[0], center[1]))
            planning_unit_grid = gpd.GeoDataFrame(geometry = hexagons, crs = Prj)
            
            planning_unit_grid["PUID"] = planning_unit_grid.index + 1
            planning_unit_grid.to_file("planning_unit_grid.shp")

            continue
        elif selection == 5:
            # 5 View on Map
            continue
        elif selection == 9:
            # 9 Return to Main Menu
            break
        else:
            print_error_msg(msg_value_error)
            continue
    return planning_unit_grid


# %% Select planning units

# def select_planning_units():
#     # ask for input()
#     extent_str = input("Enter extents as xmin ymin xmax ymax: ")
#     extent = list(map(float, extent_str.split()))

#     poly = gpd.GeoSeries([{
#         'type': 'Polygon',
#         'coordinates': [[
#             [extent[0], extent[1]],
#             [extent[2], extent[1]],
#             [extent[2], extent[3]],
#             [extent[0], extent[3]],
#             [extent[0], extent[1]]
#         ]]
#     }], crs='epsg:4326')
#     selected_hexagons = hexagons[hexagons.intersects(poly[0])]


#     userPUID = input("What is the PUID? Type the PUID's and put a space between each one':")
#     selected_hexagons = hexagons[hexagons.PUID.isin(puids.split(','))]


#     userShapefile = input("What is the path to the Shapefile?:")

#     # Find intersecting hexagons
#     selected_poly = gpd.read_file(userShapefile)
#     selected_hexagons = hexagons[hexagons.intersects(selected_poly.geometry.unary_union)]

#     userGUID = input("What is the GUID?:")

#     selected_poly = gpd.GeoDataFrame(geometry=[hexagons.unary_union])
#     selected_poly.plot()
#     plt.show()
#     selected_hexagons = hexagons[hexagons.intersects(selected_poly.geometry.unary_union)]

#     # Create new filtered gpd containing hexagons from selection
#     filtered_gpd = selected_hexagons.copy()

# # Optionally display the result of the hexagons within the area of interest.
#     if input_type == "extents" or input_type == "shapefile" or input_type == "GUI":
#         filtered_gpd.plot()
#         plt.show()

#     # 1 Interactive map
#     # 2 csv #do we want gui for this, easily done with Tkinter
#     # 3 shp/gpgk file #do we want gui for this, easily done with Tkinter
#     # 4 User Input
#         # if 1:
#         #     #display map with planning units and get input from user
#         # elif 2:
#         #     # read in csv of puids
#         # elif 3:
#         #     # read in and determine overlaps to generate list
#         # elif 4:
#             # ask user to enter puids (loop, or space seperated list)
#         #validate
#         # return puid_list
#     return


def select_planning_units(planning_unit_grid: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Author: Ethan

    Parameters
    ----------
    planning_unit_grid : gpd.GeoDataFrame
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """

    filtered_planning_unit_grid = planning_unit_grid.copy(deep=True)

    if planning_unit_grid.empty:
        print_error_msg("No planning unit grid loaded.")
        return planning_unit_grid

    while True:
        try:
            selection = int(
                input(
                    """
    Select Planning Units
        1 Manual Input
        2 Interactive
        3 Extents from File
        9 Return to Main Menu
    >>> """
                )
            )
        except ValueError:
            print_error_msg(msg_value_error)

        if selection == 1:
            # 1 Manual Input
            while True:
                try:
                    selection = int(
                        input(
                            """
    Select Planning Units Manual Input Menu
        1 Extents
        2 PUIDS
        3 Extents from File
        9 Return to Select Planning Units Menu
    >>> """
                        )
                    )
                except ValueError:
                    print_error_msg(msg_value_error)

                if selection == 1:
                    # 1 Extents
                    extent_str = input("Enter extents as xmin ymin xmax ymax: ")
                    extent = list(map(float, extent_str.split()))

                    poly = gpd.GeoSeries([{
                        'type': 'Polygon',
                        'coordinates': [[
                            [extent[0], extent[1]],
                            [extent[2], extent[1]],
                            [extent[2], extent[3]],
                            [extent[0], extent[3]],
                            [extent[0], extent[1]]
                        ]]
                    }], crs='epsg:4326')
                    selected_hexagons = filtered_planning_unit_grid[hexagons.intersects(poly[0])]
                    break
                elif selection == 2:
                    # 2 PUIDS
                    userPUID = input("What is the PUID? Type the PUID's and put a space between each one':")
                    selected_hexagons = hexagons[hexagons.PUID.isin(puids.split(','))]
                    break
                elif selection == 3:
                    # 3 Extents from File
                    userShapefile = input("What is the path to the Shapefile?:")
                    # Find intersecting hexagons
                    selected_poly = gpd.read_file(userShapefile)
                    selected_hexagons = hexagons[hexagons.intersects(selected_poly.geometry.unary_union)]
                    break
                
                elif selection == 9:
                    # 9 Return to Main Menu
                    break
                else:
                    print_error_msg(msg_value_error)
                    continue

        elif selection == 2:
            # 2 Interactive
            continue
        elif selection == 3:
            # 3 Grid from File
            continue
        elif selection == 9:
            # 9 Return to Main Menu
            break
        else:
            print_error_msg(msg_value_error)
            continue

    return filtered_planning_unit_grid


# %% Load planning layers from file


def load_planning_layers(planning_layers: list) -> list[gpd.GeoDataFrame]:
    """
    Author: Nata

    Parameters
    ----------
    planning_layers : list
        DESCRIPTION.

    Returns
    -------
    planning_layers : TYPE
        DESCRIPTION.

    """
    # get list of files to load
    while True:
        try:
            selection = int(
                input(
                    """
    Load Planning Layers
        1 All from Directory
        2 Select Files
        3 Remove Layers
        4 View Layers on Map
        9 Return to Main Menu
    >>> """
                )
            )
        except ValueError:
            print_error_msg(msg_value_error)

        if selection == 1:
            # 1 All from Directory
            continue
        elif selection == 2:
            # 2 Select Files
            files = get_files(title="Select planning layer files")
            for file in files:
                planning_layers.append(gpd.read_file(file))
            break
        elif selection == 3:
            # 3 Remove Layers
            continue
        elif selection == 4:
            # 4 View layers on Map
            continue
        elif selection == 9:
            # 9 Return to Main Menu
            break
        else:
            print_error_msg(msg_value_error)
            continue
    return planning_layers


# %% Filter for specific conservation features


def query_planning_layers(
    planning_layers: list[gpd.GeoDataFrame],
) -> list[gpd.GeoDataFrame]:
    """
    Author: Nata

    Parameters
    ----------
    planning_layers : list[gpd.GeoDataFrame]
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """

    filtered_planning_layers = []

    if not len(planning_layers):
        print_error_msg("No planning layers loaded.")
        return []

    filtered_planning_layers = []
    for layer in planning_layers:
        filtered_planning_layers.append(layer.copy(deep=True))

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
        9 Return to Main Menu
    >>> """
                )
            )
        # 5 By Area --> Not sure about this one, could produce another menu
        # to get extents from intput, file, or interactive on map, but that
        # may be redundant if we just limits to the bounds of the selected
        # planning units to start with.
        except ValueError:
            print_error_msg(msg_value_error)

        if selection == 1:
            # 1 ID
            continue
        elif selection == 2:
            # 2 CLASS_TYPE
            continue
        elif selection == 3:
            # 3 GROUP_
            continue
        elif selection == 4:
            # 3 NAME
            continue
        elif selection == 9:
            # 9 Return to Main Menu
            break
        else:
            print_error_msg(msg_value_error)
            continue

    return filtered_planning_layers


# %% Calculate planning unit / conservation feature overlap


def calc_overlap(planning_grid: gpd.GeoDataFrame, cons_layers: list[gpd.GeoDataFrame]) -> list[gpd.GeoDataFrame]:
    """
    Author: Mitch

    Parameters
    ----------
    planning_grid : gpd.GeoDataFrame
        DESCRIPTION.
    cons_layers : list[gpd.GeoDataFrame]
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """

    if not len(cons_layers):
        print_error_msg("No planning layers loaded.")
        return []
    if planning_grid.empty:
        print_error_msg("No planning layers loaded.")
        return []

    intersections = []

    for layer in cons_layers:
        # can add crs check here
        intersection = gpd.overlay(planning_grid, layer, how="intersection")
        # add intersection gdf to list
        intersection[AREA_X] = intersection.area
        intersections.append(intersection)

    return intersections


# def getArgs() -> argparse.ArgumentParser:
#     """
#     Adds command line arguments to the program.

#     Returns
#     -------
#     argparse.ArgumentParser
#         Contains passed command line arguments.

#     """

#     # create parser
#     parser = argparse.ArgumentParser()
#     # add arguments here
#     return parser.parse_args()


# def create_planning_unit(hex_size: float, grid_size: float , pos: tuple(float, float)) -> gpd.geoseries:
#     pass

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
            user_input = input(f"The CRS '{crs}' does not match the target CRS '{target_crs}'. Would you like to correct it? [y/n]: ")
            if user_input.lower() == 'y':
                # If the user wants to correct it, prompt for the correct CRS and check if it matches the target CRS
                corrected_crs = input("Enter the corrected CRS: ")
                if corrected_crs == target_crs:
                    return True
                else:
                    print(f"The corrected CRS '{corrected_crs}' does not match the target CRS '{target_crs}'. Validation failed.")
                    return False
            else:
                # If the user doesn't want to correct it, fail the validation
                print("Validation failed.")
                return False
    elif isinstance(crs, dict):
        # If crs is a dictionary, check if it has a 'crs' key and if its value matches the target CRS
        if 'crs' in crs:
            if crs['crs'] == target_crs:
                return True
            else:
                # If it doesn't match, prompt the user to either correct it or fail
                user_input = input(f"The CRS '{crs['crs']}' does not match the target CRS '{target_crs}'. Would you like to correct it? [y/n]: ")
                if user_input.lower() == 'y':
                    # If the user wants to correct it, prompt for the correct CRS and check if it matches the target CRS
                    corrected_crs = input("Enter the corrected CRS: ")
                    if corrected_crs == target_crs:
                        crs['crs'] = corrected_crs
                        return True
                    else:
                        print(f"The corrected CRS '{corrected_crs}' does not match the target CRS '{target_crs}'. Validation failed.")
                        return False
                else:
                    # If the user doesn't want to correct it, fail the validation
                    print("Validation failed.")
                    return False
        else:
            # If the dictionary doesn't have a 'crs' key, prompt the user to either correct it or fail
            user_input = input("The input dictionary does not have a 'crs' key. Would you like to add it and enter a CRS? [y/n]: ")
            if user_input.lower() == 'y':
                # If the user wants to add a 'crs' key, prompt for the CRS and check if it matches the target CRS
                corrected_crs = input("Enter the CRS: ")
                if corrected_crs == target_crs:
                    crs['crs'] = corrected_crs
                    return True
                else:
                    print(f"The entered CRS '{corrected_crs}' does not match the target CRS '{target_crs}'. Validation failed.")


# %% Main


def main():
    """
    Author: Mitch

    Returns
    -------
    int
        DESCRIPTION.

    """

    def main_menu():
        """
        Author: Mitch

        Returns
        -------
        None.

        """
        planning_unit_grid = gpd.GeoDataFrame()
        filtered_planning_unit_grid = gpd.GeoDataFrame()
        planning_layers = []  # gpd.GeoDataFrame()
        filtered_planning_layers = []  # gpd.GeoDataFrame()
        intersections_gdf = []
        intersections_df = pd.DataFrame()

        while True:
            try:
                selection = int(
                    input(
                        """
    Main Menu:
        1 Create Planning Unit Grid
        2 Select Planning Units
        3 Load Planning Layers
        4 Select Conservation Features
        5 View Layers
        6 Calculate Overlap
        7 Save Results
        9 Quit
    >>> """
                    )
                )
            except ValueError:
                print_error_msg(msg_value_error)

            if selection == 1:
                planning_unit_grid = create_planning_unit_grid(planning_unit_grid)
                continue
            elif selection == 2:
                filtered_planning_unit_grid = select_planning_units(planning_unit_grid)
                continue
            elif selection == 3:
                # load planning layers
                planning_layers = load_planning_layers(planning_layers)
                continue
            elif selection == 4:
                # select conservation features
                filtered_planning_layers = query_planning_layers(planning_layers)
                continue
            elif selection == 5:
                # View Layers
                continue
            elif selection == 6:
                # Calculate Overlap
                # intersections_gdf = calc_overlap(
                #     filtered_planning_unit_grid, filtered_planning_layers
                # )
                intersections_gdf = calc_overlap(planning_unit_grid, planning_layers)
                if len(intersections_gdf):
                    intersections_df = pd.DataFrame(gpd.GeoDataFrame(pd.concat(intersections_gdf, ignore_index=True)))
                continue
            elif selection == 7:
                # Save Results
                if intersections_df.empty:
                    print_error_msg("No results to save.")
                    continue
                file_name = get_save_file_name(title="Save results to csv", f_types=ft_csv)
                intersections_df.to_csv(file_name, columns=[PUID, ID, AREA_X], index=False)
                continue
            elif selection == 9:
                # quit
                break
        return

    # start the main menu thread

    def server_thread():
        app.app.run()
        return

    server = threading.Thread(target=server_thread)
    main_menu_thread = threading.Thread(target=main_menu)

    server.start()
    sleep(0.1)
    main_menu_thread.start()
    main_menu_thread.join()

    if server.is_alive():
        server.join(1.0)

    print("All done!")

    return 0


if __name__ == "__main__":
    if run_tests:
        input("\nTESTING COMPLETE")
    else:
        main()
