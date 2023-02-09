#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""
# Import modules
import os
import pandas as pd
os.environ["USE_PYGEOS"] = "0"
import geopandas as gpd
import argparse


# Global Variables
run_tests = False
verbose = True

default_crs = 0
planning_unit = 0 #gpd.GeoDataFrame()
planning_layers = [] #list(gpd.GeoDataFrame())


def getArgs() -> argparse.ArgumentParser:
    """
    Adds command line arguments to the program.

    Returns
    -------
    argparse.ArgumentParser
        Contains passed command line arguments.

    """

    # create parser
    parser = argparse.ArgumentParser()
    # add arguments here
    return parser.parse_args()

def validate_crs(crs: any, target_crs:str) -> bool:
    pass

def create_planning_unit(hex_size: float, grid_size: float , pos: tuple(float, float)) -> gpd.geoseries:
    pass

def select_planning_units() -> list(int):
    # ask for input()
    # 1 Interactive map
    # 2 csv #do we want gui for this, easily done with Tkinter
    # 3 shp/gpgk file #do we want gui for this, easily done with Tkinter
    # 4 User Input
        # if 1:
        #     #display map with planning units and get input from user
        # elif 2:
        #     # read in csv of puids
        # elif 3:
        #     # read in and determine overlaps to generate list
        # elif 4:
            # ask user to enter puids (loop, or space seperated list)
        #validate
        # return puid_list
    pass

def select_planning_layers_to_load() ->list():
	#get user input()
	    #while loop to load files manually
	#or profide
	# dir to load all files (include file type filter options)
    # or single or list of space seperated file paths

    #do we want gui for this, easily done with Tkinter
    return

def load_planning_layers() -> bool:
    #gpd.read_file()
    pass

def query_planning_layers() -> list(gpd.GeoDataFrame):
    # get input()
    # show list or groups?
    # area selection on map?
    #probably easiest with gui here also???
    pass

def calc_overlap() -> list(list(float)): # -> PUID by CFID matrix, overlap area as values:
    pass

def to_marxan_format() -> list((float,float)):  # -> list of PUID, CFID tuples
    pass

def marxan_format_to_csv(arr:list((float,float))) -> bool:
    return True


def main():
    """
    Parameters
    ----------

    Returns
    -------
    int
        0 for success, -1 for error
    """
    # get arguments from argparser
    args = getArgs()
    # extract and validate args here for clarity

    # Create a planning unit hexagonal grid with user input on hexagon size and grid size and position.
    create_planning_unit()

    # Take input on which planning unit(s) the proponent project will occupy
    select_planning_units()

    # Select planning layers to load
    select_planning_layers_to_load()

    # Load planning layers
    load_planning_layers()

    # Query for relevant planning features to use in the analysis
    query_planning_layers()

    # For each project PUID, calculate the area of overlap with the each conservation feature (CF) from the
    # planning layer and record this in a csv - a sparse matrix of PUID (rows) vs CFID (cols) with overlap
    # area as values.
    calc_overlap()

    # Reorganize the file so it can be ingested by Marxan
    to_marxan_format()

    #save to csv
    marxan_format_to_csv()

    if verbose:
        print("Complete")

    return 0


if __name__ == "__main__":

    if run_tests:
        input("\nTESTING COMPLETE")
    else:
        main()
