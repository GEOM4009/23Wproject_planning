# -*- coding: utf-8 -*-
"""
planning.py
Authors: Mitch, Lucas, Ethan, Nata, Winaa

This file contains the main script for the GEOM4009 planning project.
It contains the main menu and all the functions for the different the
different steps of the data and planning process.

NOTE: This script must be run in the geom4009 environment, but will require
    the installation of the following additional packages:

    conda install -c anaconda flask  --> this will be removed in the future
    conda install -c conda-forge tk  --> provides the tkinter GUI
    conda install -c conda-forge h3-py --> provides the h3 hexagonal grid package

TODO: Get user input to set CRS for the project
TODO: Confirm with client if there will be any use case for an argument parser
TODO: Add additional error handling for the different functions

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
import h3
from math import pi, cos


os.environ["USE_PYGEOS"] = "0"
import geopandas as gpd
import pandas as pd


# Global Variables
run_tests = False
verbose = True

# %% create a planning unit grid


def create_planning_unit_grid(planning_unit_grid) -> gpd.GeoDataFrame:
    """
    Author: Lucas
    This function will take user input to create a hexagonal planning
    grid that is defined by a central coordinate, cell resolution,
    and grid height and width. A unique Planning unit ID is then given
    to each hexagon and the final grid can be output to a shapefile.
    Parameters
    ----------
    planning_unit_grid : gpd.geodataframe
        if a previuos hexagonal grid has been created it can be input
        to skip the creation of a new grid

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
            # This will be the primary method of input as it requires
            # the least amount of prerequisite data
            # The inputs below will get the information needed to
            # create a boundary for the hexagon to be creaetd in as
            # well as define the hexagon cell size
            resolution = get_user_float(
                """
    Enter a Grid Resolution (0-15),
        Edge length for each resolution:
        0(1107km), 1(418km), 2(158km), 3(59.8km),
        4(22.6km), 5(8.54km), 6(3.23km), 7(1.22km),
        8(461m), 9(174m), 10(65.9m), 11(24.9m),
        12(9.41m), 13(3.56m), 14(1.35m), 15(0.509m): """
            )
            grid_size_x = get_user_float("Grid Size X (km): ")
            grid_size_y = get_user_float("Grid Size Y (km): ")
            grid_lat = get_user_float("Latitude of grid anchor point (dd): ")
            grid_lon = get_user_float("Longitude of grid anchor point (dd): ")
            # Half of the grid width and height can be added to the central
            # coordinate to create a study area that meets the criteria
            xdiff = grid_size_x / 2
            ydiff = grid_size_y / 2

            xmax = grid_lon + (180 / pi) * (xdiff / 6378137) / cos(grid_lat)
            xmin = grid_lon - (180 / pi) * (xdiff / 6378137) / cos(grid_lat)
            ymax = grid_lat + (180 / pi) * (ydiff / 6378137)
            ymin = grid_lat - (180 / pi) * (ydiff / 6378137)
            # dictionary is created that contains the boundary points above to define a polygon
            geo = {
                "type": "Polygon",
                "coordinates": [
                    [
                        [xmin, ymin],
                        [xmin, ymax],
                        [xmax, ymax],
                        [xmax, ymin],
                        [xmin, ymin],
                    ]
                ],
            }
            # Hexagonal grid is iterated through the study region file, with
            # resolution used to define the grid cell size
            hexes = h3.polyfill(geo, resolution)
            # data frame is created that contains the set of hexagon
            # cell ids obtained above
            df = pd.DataFrame(list(hexes))
            # Column renamed from 0 to Hex ID
            df.columns = ["Hex_ID"]
            # unique PUID is assigned to each hexagon
            df["PUID"] = df.index + 1
            #           #function is defined that converts the Hex ID into a hexagon geometry
            def add_geometry(row):
                points = h3.h3_to_geo_boundary(row["Hex_ID"], True)
                return Polygon(points)

            # function above is used to create the geometry column
            df["geometry"] = df.apply(add_geometry, axis=1)
            # df is turned into a geodataframe with the geometry column as the geometry
            # The CRS used is albers equal area as that is the one the client uses
            # In the future the CRS will be defined by user input
            planning_unit_grid = gpd.GeoDataFrame(
                df, geometry=df["geometry"], crs="epsg:9822"
            )
            #           #final planning grid is exported to shapefile so it can be reused in the future
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
#         print_error_msg("No planning unit grid loaded.")
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
#             print_error_msg(msg_value_error)

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
#                     print_error_msg(msg_value_error)

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
#                     print_error_msg(msg_value_error)
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
#             print_error_msg(msg_value_error)
#             continue

#     return filtered_planning_unit_grid


# %% Load planning layers from file


def load_planning_layers(planning_layers: list) -> list[gpd.GeoDataFrame]:
    """
    Author: Nata

    Takes user selection to load planning/ conservation layers of interest

    Parameters
    ----------
    planning_layers : list
        Takes a list of planning layers to load.

    Returns
    -------
    planning_layers : TYPE
        returns a geodataframe of the selected planning layers.

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
            # Call Mitch's util function to load all files from the selected directory
            files = get_files_from_dir()
            for file in files:
                planning_layers.append(gpd.read_file(file))
            break
        elif selection == 2:
            # 2 Select Files
            # Call Mitch's util function to load selected file(s) from user input (popup)
            files = get_files(title="Select planning layer files")
            for file in files:
                planning_layers.append(gpd.read_file(file))
            break
            # planning_layers=get_files()
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

        Takes planning layers and user input on conservation features of interest to select by attribute and save new file

    NOTE this is not fully functional yet, it keeps returning empty files, but is close to solving!

        Parameters
        ----------
        planning_layers : list[gpd.GeoDataFrame]
            Takes the pre-loaded planning layers file.

        Returns
        -------
        TYPE
            Returns a geodataframe of only the selected conservation features.

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
            # then filter by ID
            # make empty list to fill with the unique values in planning layers ID field, to show user
            filter = []
            # loop through the geodataframes to find and save every unique ID value, save to the filter list
            for gdf in planning_layers:
                filter.extend(gdf["ID"].unique())
            # get user to select ID of interest
            # NOTE this is currently for selection of single features, but will be expanded to multi later
            # filterValues is essentially a list with one value for now
            chosenFeature = get_user_selection(filter)
            # do the filtering - loop through planning layers, keeping rows that match chosenFeature
            for i in range(len(filtered_planning_layers)):
                # filter by checking if the ID value is in the chosenFeature list
                filtered_planning_layers[i] = filtered_planning_layers[i][
                    filtered_planning_layers[i]["ID"].isin(chosenFeature)
                ]
                # this does not fully work, it keeps returning an empty list of geodataframes, will solve for the next report

            continue
        elif selection == 2:
            # 2 CLASS_TYPE
            # then filter by class type
            # make empty list to fill with the unique values in planning layers CLASS_TYPE field, to show user
            filter = []
            # loop through the geodataframes to find and save every unique CLASS_TYPE value, save to the filter list
            for gdf in planning_layers:
                filter.extend(gdf["CLASS_TYPE"].unique())
            # get user to select class of interest
            # NOTE this is currently for selection of single features, but will be expanded to multi later
            # filterValues is essentially a list with one value for now
            chosenFeature = get_user_selection(filter)
            # do the filtering - loop through planning layers, keeping rows that match chosenFeature
            for i in range(len(filtered_planning_layers)):
                # filter by checking if the CLASS_TYPE value is in the chosenFeature list
                filtered_planning_layers[i] = filtered_planning_layers[i][
                    filtered_planning_layers[i]["CLASS_TYPE"].isin(chosenFeature)
                ]
                # this does not fully work, it keeps returning an empty list of geodataframes, will solve for the next report

            continue
        elif selection == 3:
            # 3 GROUP_
            # Then filter by group
            # make empty list to fill with the unique values in planning layers GROUP_ field, to show user
            filter = []
            # loop through the geodataframes to find and save every unique GROUP_ value, save to the filter list
            for gdf in planning_layers:
                filter.extend(gdf["GROUP_"].unique())
            # get user to select GROUP_ of interest
            # NOTE this is currently for selection of single features, but will be expanded to multi later
            # filterValues is essentially a list with one value for now
            chosenFeature = get_user_selection(filter)
            # do the filtering - loop through planning layers, keeping rows that match chosenFeature
            for i in range(len(filtered_planning_layers)):
                # filter by checking if the group value is in the chosenFeature list
                filtered_planning_layers[i] = filtered_planning_layers[i][
                    filtered_planning_layers[i]["GROUP_"].isin(chosenFeature)
                ]
                # this does not fully work, it keeps returning an empty list of geodataframes, will solve for the next report
            continue

        elif selection == 4:
            # 3 NAME
            # Then filter by name
            # make empty list to fill with the unique values in planning layers NAME field, to show user
            filter = []
            # loop through the geodataframes to find and save every unique NAME value, save to the filter list
            for gdf in planning_layers:
                filter.extend(gdf["NAME"].unique())
            # get user to select ID of interest
            # NOTE this is currently for selection of single features, but will be expanded to multi later
            # filterValues is essentially a list with one value for now
            chosenFeature = get_user_selection(filter)
            # do the filtering - loop through planning layers, keeping rows that match chosenFeature
            for i in range(len(filtered_planning_layers)):
                # filter by checking if the name value is in the chosenFeature list
                filtered_planning_layers[i] = filtered_planning_layers[i][
                    filtered_planning_layers[i]["NAME"].isin(chosenFeature)
                ]
                # this does not fully work, it keeps returning an empty list of geodataframes, will solve for the next report
            continue

        elif selection == 9:
            # 9 Return to Main Menu
            break
        else:
            print_error_msg(msg_value_error)
            continue

    return filtered_planning_layers


# %% Calculate planning unit / conservation feature overlap


def calc_overlap(
    planning_grid: gpd.GeoDataFrame, cons_layers: list[gpd.GeoDataFrame]
) -> list[gpd.GeoDataFrame]:
    """
    Author: Mitch
    Intersects planning grid with conservation layers and calculates area of overlap.
    Parameters
    ----------
    planning_grid : gpd.GeoDataFrame
        The planning grid to intersect with conservation layers.
    cons_layers : list[gpd.GeoDataFrame]
        A list of conservation layers containing only the desired conservation features
        to intersect with the planning grid.

    Returns
    -------
    list[gpd.GeoDataFrame] | list[]
        The intersected gdfs, or an empty list if planning grid or conservation layers are not loaded,
        or if there are no intersecting features.

    """

    # check if planning grid and conservation layers are loaded, otherwise return empty list
    if not len(cons_layers):
        print_error_msg("No planning layers loaded.")
        return []
    if planning_grid.empty:
        print_error_msg("No planning layers loaded.")
        return []

    # initialize list to hold intersection gdfs
    intersections = []

    # for each conservation layer, calculate intersection with planning grid
    for layer in cons_layers:
        # TODO: check if planning grid and conservation layer are in same CRS
        # TODO: confirm name of area column

        # intersect planning grid and conservation layer, add area column, and append to list
        intersection = gpd.overlay(planning_grid, layer, how="intersection")
        intersection[AREA_X] = intersection.area  # confirm name
        intersections.append(intersection)

    return intersections


# %% CRS helper function


def validate_crs(crs: any, target_crs: str) -> bool:
    """
    Author: Winaa

    Parameters
    ----------
    crs : any
        DESCRIPTION.
    target_crs : str
        DESCRIPTION.

    Returns
    -------
    bool
        DESCRIPTION.

    """
    return


# %% Main


def main():
    """
    Author: Mitch
    Main function. Calls main_menu() and runs until user enters 9 to exit.
    Currently setup to run as a seperate thread to allow for the flask server,
    but this will be removed.

    """

    def main_menu():
        """
        Author: Mitch
        Prints main menu and returns user selection. If user selection is not
        valid, will print error message and return to main menu. If user
        enters 9, will exit program. Otherwise calls appropriate function based
        on user selection.

        NOTE: This function is currently run as a seperate thread to allow
         for the flask server to run at the same time as the main menu. However,
         based on feedback from the client, the flask server may be removed as the
         usecase for it is not needed.

        Returns
        -------
        None.

        """
        # intialize variables
        planning_unit_grid = gpd.GeoDataFrame()  # planning unit grid
        filtered_planning_unit_grid = (
            gpd.GeoDataFrame()
        )  # this is the planning unit grid after filtering, now obsolete
        planning_layers = (
            []
        )  # list of planning layers gdfs, name will change to conservation_features
        filtered_planning_layers = (
            []
        )  # this is list of conservation_features gdfs after filtering
        intersections_gdf = (
            []
        )  # list of gdfs of planning unit / conservation feature intersections
        intersections_df = (
            pd.DataFrame()
        )  # dataframe of planning unit / conservation feature intersections, used to easy csv export

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
                # 1 Create Planning Unit Grid
                planning_unit_grid = create_planning_unit_grid(planning_unit_grid)
                continue
            elif selection == 2:
                # 3 Select Planning Units
                # NOTE: this is now obsolete, but only commenting out for now
                # filtered_planning_unit_grid = select_planning_units(planning_unit_grid)
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
                # TODO: add function to view layers on map
                #       maybe helpful but will not need to be in final product
                continue
            elif selection == 6:
                # Calculate Overlap
                # TODO: update to remove filtered_planning_unit_grid
                # intersections_gdf = calc_overlap(
                #     filtered_planning_unit_grid, filtered_planning_layers
                # )
                intersections_gdf = calc_overlap(planning_unit_grid, planning_layers)
                if len(intersections_gdf):
                    intersections_df = pd.DataFrame(
                        gpd.GeoDataFrame(
                            pd.concat(intersections_gdf, ignore_index=True)
                        )
                    )
                continue
            elif selection == 7:
                # Save Results
                # TODO: add saving of planning unit grid
                if intersections_df.empty:
                    print_error_msg("No results to save.")
                    continue
                file_name = get_save_file_name(
                    title="Save results to csv", f_types=ft_csv
                )
                # Columns names / order need to be updated to match sample file from client, waiting to receive
                intersections_df.to_csv(
                    file_name, columns=[PUID, ID, AREA_X], index=False
                )
                continue
            elif selection == 9:
                # quit
                # TODO: add confirmation prompt if user has not saved results
                break
        return

    # def server_thread():
    #     """
    #     Runs the flask server in a seperate thread.
    #     Note: This will be removed.
    #     """
    #     app.app.run()
    #     return

    # server = threading.Thread(target=server_thread)

    main_menu_thread = threading.Thread(target=main_menu)

    # server.start()
    # sleep(0.1)
    main_menu_thread.start()
    main_menu_thread.join()

    # if server.is_alive():
    #    server.join(1.0)

    print("All done!")

    return


if __name__ == "__main__":
    if run_tests:
        input("\nTESTING COMPLETE")
    else:
        main()

# %%
