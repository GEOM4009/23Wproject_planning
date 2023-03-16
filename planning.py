# -*- coding: utf-8 -*-
"""
"""
# Import modules
from tkinter import *
from util import *
from defs import *
import argparse
import os
from shapely.geometry import Polygon
import h3
import math

os.environ["USE_PYGEOS"] = "0"
import geopandas as gpd
import pandas as pd

# Global Variables
run_tests = False
verbose = True


def create_planning_unit_grid():

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
    >>>"""
                )
            )
            if selection == 1:
                # 1 Manual Input
                resolution = get_user_float(f"Enter a Grid Resolution (0-15),\
                            Edge length for each resolution:\
                            0(1107km), 1(418km), 2(158km), 3(59.8km),\
                            4(22.6km), 5(8.54km), 6(3.23km), 7(1.22km),\
                            8(461m), 9(174m), 10(65.9m), 11(24.9m),\
                            12(9.41m), 13(3.56m), 14(1.35m),'15(0.509m),: ")
                grid_size_x = get_user_float("Grid Size X (km): ")
                grid_size_y = get_user_float("Grid Size Y (km): ")
                grid_lat = get_user_float("Latitude of grid anchor point (dd): ")
                grid_lon = get_user_float("Longitude of grid anchor point (dd): ")

                xdiff = grid_size_x/2
                ydiff = grid_size_y/2

                xmax =  grid_lon + (180/pi)*(xdiff/6378137)/cos(lat0)
                xmin =  grid_lon - (180/pi)*(xdiff/6378137)/cos(lat0)
                ymax = grid_lat + (180/pi)*(ydiff/6378137)
                ymin = grid_lat - (180/pi)*(ydiff/6378137)
                geo = {'type': 'Polygon',
                        'coordinates': [
                            [   [xmin, ymin],
                                [xmin, ymax],
                                [xmax, ymax],
                                [xmax, ymin],
                                [xmin, ymin]]]}

                hexes = h3.polyfill(geo, resolution)
                df = pd.DataFrame(list(hexes))
                df.columns = ['Hex_ID']
                df['PUID'] = df.index + 1
                def add_geometry(row):
                  points = h3.h3_to_geo_boundary(row['Hex_ID'], True)
                  return Polygon(points)

                df['geometry'] = (df.apply(add_geometry,axis=1))
                planning_unit_grid = gpd.GeoDataFrame(df, geometry=df['geometry'], crs = "epsg:")
                planning_unit_grid.to_file('planning_unit_grid.shp')
                continue
            elif selection == 2:
                # 2 Interactive
                continue
            elif selection == 3:
                # 3 Grid from File
                continue
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
        except ValueError:
            print_error_msg(msg_value_error)
    return

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
    >>>"""
                )
            )
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
    >>>"""))
                        if selection == 1:
                            # 1 Extents
                            break
                        elif selection == 2:
                            # 2 PUIDS
                            break
                        elif selection == 3:
                            # 3 Extents from File
                            break
                        elif selection == 9:
                        # 9 Return to Main Menu
                            break
                        else:
                            print_error_msg(msg_value_error)
                            continue
                    except ValueError:
                        print_error_msg(msg_value_error)

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
        except ValueError:
            print_error_msg(msg_value_error)

    return filtered_planning_unit_grid


def load_planning_layers() -> list[gpd.GeoDataFrame]:
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
    >>>"""
                )
            )
            if selection == 1:
                # 1 All from Directory
                continue
            elif selection == 2:
                # 2 Select Files
                continue
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
        except ValueError:
            print_error_msg(msg_value_error)
    return


def query_planning_layers(
    planning_layers: list[gpd.GeoDataFrame],
) -> list[gpd.GeoDataFrame]:

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
    >>>"""
                )
            )
            # 5 By Area --> Not sure about this one, could produce another menu
            # to get extents from intput, file, or interactive on map, but that
            # may be redundant if we just limits to the bounds of the selected
            # planning units to start with.
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
        except ValueError:
            print_error_msg(msg_value_error)

    return filtered_planning_layers


def calc_overlap(
    planning_grid: gpd.GeoDataFrame, cons_layers: list[gpd.GeoDataFrame]
) -> list[gpd.GeoDataFrame]:

    if not len(cons_layers):
        print_error_msg("No planning layers loaded.")
        return []
    if planning_grid.empty:
        print_error_msg("No planning layers loaded.")
        return []

    intersections = []

    for layer in cons_layers:
        # can add crs check here
        intersection = gpd.overlay(planning_grid, cons_layers, how="intersection")
        # add intersection gpd to list
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


def validate_crs(crs: any, target_crs: str) -> bool:
    return


def main():
    """
    Parameters
    ----------

    Returns
    -------
    int
        0 for success, -1 for error
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
    >>>"""
                )
            )
            if selection < 1 or selection > 4:
                print_error_msg(msg_value_error)
                continue
            if selection == 1:
                planning_unit_grid = create_planning_unit_grid()
                continue
            elif selection == 2:
                filtered_planning_unit_grid = select_planning_units(planning_unit_grid)
                continue
            elif selection == 3:
                # load planning layers
                planning_layers = load_planning_layers()
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
                intersections_gdf = calc_overlap(
                    filtered_planning_unit_grid, filtered_planning_layers
                )
                if len(intersections_gdf):
                    intersections_df = pd.DataFrame(
                        gpd.GeoDataFrame(pd.concat(intersections_gdf, ignore_index=True))
                    )
                continue
            elif selection == 7:
                # Save Results
                if intersections_df.empty:
                    print_error_msg("No results to save.")
                    continue
                file_name = get_save_file_name(title="Save Results to csv", f_types=ft_csv )
                intersections_df.to_csv("output.csv", columns=[PUID, ID, AREA_X])
                continue
            elif selection == 9:
                # quit
                break

        except ValueError:
            print_error_msg(msg_value_error)

    return 0


if __name__ == "__main__":
    if run_tests:
        input("\nTESTING COMPLETE")
    else:
        main()
