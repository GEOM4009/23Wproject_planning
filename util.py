# -*- coding: utf-8 -*-
"""
util.py

This file contains utility functions for the planning.py script

@author: Mitch Albert

Revision History:
    MA: 2021-02-09: Initial version
                    Added get_file function
                    Added get_files function
"""


from os import getcwd
import tkinter.filedialog
from typing import List


# filedialog file types
ft_shapefile = ("Shapefile", "*.shp")
ft_geo_package = ("GeoPackage ", "*.gpkg")
ft_geodatabase = ("File Geodatabase", "*.gdb")
ft_csv = ("Comma-separated values", "*.csv")
ft_json = ("Json", ("*.geojson", "*.json"))
ft_kml = ("Keyhole Markup Language", "*.KML")
ft_any = ("All files", "*.*")
ft_standard = [ft_shapefile, ft_geo_package, ft_any]
ft_all = [ft_any, ft_csv, ft_json, ft_shapefile, ft_geo_package, ft_kml]


def get_file(
    f_types: tuple[str, str] | list[tuple[str, str]] = ft_standard,
    title: str = "Select File To Load",
    initialdir=getcwd(),
) -> str:
    """
    Retrieves a single file using a tkinter file dialog.

    Parameters
    ----------
    f_types : tuple[str, str] | list[tuple[str, str]], optional
        The file type(s) allowed. The default is standard_types.
    title : str, optional
        Title of the dialog box. Default is "Select File To Load".

    Returns
    -------
    str
        A str that is pathlike, or None if cancel is selected.
    """
    file = get_files(f_types, title=title, initialdir=initialdir, multi=False)
    if file != None:
        file = file[0]
    return file


def get_files(
    f_types: tuple[str, str] | list[tuple[str, str]] = ft_standard,
    title: str = "Select Files To Load",
    initialdir=getcwd(),
    multi: bool = True,
) -> List[str]:
    """
    Retrieves a list of file(s) using a tkinter file dialog.

    Parameters
    ----------
    f_types : tuple[str, str] | list[tuple[str, str]], optional
        The file type(s) allowed. The default is standard_types.
    title : str, optional
        Title of dialog box. Default is "Select Files To Load".

    Returns
    -------
    List[str]
        A list of str's that is pathlike, or None if cancel is selected
    """
    if not isinstance(f_types, list):
        f_types = [f_types]
    files = list(
        tkinter.filedialog.askopenfilename(
            initialdir=initialdir, title=title, filetypes=f_types, multiple=multi
        )
    )
    if not len(files):
        files = None
    return files



if __name__ == "__main__":





    print(get_file(ft_csv, title="This is a demo"))