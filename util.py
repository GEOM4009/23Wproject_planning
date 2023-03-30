# -*- coding: utf-8 -*-
"""
util.py

This file contains utility functions for the planning.py script

@author: Mitch Albert

Revision History:
    MA: 2023-02-09: Initial version
                    Added get_file()
                    Added get_files()
    MA: 2023-02-16: Added save_file()
                    Added get_user_selection()
    MA: 2023-02-20: Added get_files_from_dir()
    MA: 2023-03-23: Added print ulitity functions
                    Added progress functions
                    Added Load files function
"""

from os import getcwd, chdir, path, environ

environ["USE_PYGEOS"] = "0"
import tkinter.filedialog
from tkinter import Tk, Frame, Listbox, Scrollbar, Button
from tkinter.constants import *
from typing import List
from glob import glob
from defs import *
import threading
from time import sleep
import geopandas as gpd

# globals
stop_progress = False  # bollean to stop the progress thread


def print_progress_start(
    msg: str = msg_processing, dots: int = 10, time: float = 1
) -> threading.Thread:
    """
    Author: Mitch Albert
    Provides a progress indicator in the terminal. The progress indicator is a the
    msg string followed by a series of dots. The dots are printed at a rate of time
    seconds per dot. The number of dots is controlled by the dots parameter.

    Parameters
    ----------
    msg : str, optional
        The msg string is printed before the dots. The default is msg_processing.
    dots : int, optional
        The number of dots to prints before resetting back to the message string. The default is 10.
    time : float, optional
        The time in seconds between each dot. The default is 1.

    Returns
    -------
    prog_thread : threading.Thread
        The progress thread handle. This is required to stop the progress indicator.
    """

    def back(spaces: int) -> str:
        """
        Author: Mitch Albert
        Utility function to move the cursor back a number of spaces. This is used to
        remove the dots printed by the progress indicator.

        Parameters
        ----------
        spaces : int
            The number of spaces to move the cursor back.
        Returns
        -------
        str
            The character string to move the cursor back 'spaces' spaces.
        """
        return f"\x1b[{spaces}D"

    def progress_thread(msg: str, dots: int, time: float):
        """
        Author: Mitch Albert
        Internal thread function to print the progress dots while the work is being done.
        Parameters
        ----------
        msg : str
            The msg string is printed before the dots.
        dots : int
            The number of dots to prints before resetting back to the message string.
        time : float
            The time in seconds between each dot.
        Returns
        -------
        None.
        """
        count = 0
        print(msg, end="")
        while not stop_progress:
            if count and count % (dots + 1) == 0:
                print(back(dots) + " " * dots + back(dots + 1), end="")
            print(".", end="", flush=True)
            count += 1
            sleep(time)
        print("", flush=True)
        return

    global stop_progress
    stop_progress = False
    prog_thread = threading.Thread(
        target=progress_thread,
        args=(
            msg,
            dots,
            time,
        ),
    )
    prog_thread.start()
    return prog_thread


def print_progress_stop(thread: threading.Thread) -> None:
    """
    Author: Mitch Albert
    Stops the progress indicator thread, using the thread handle returned by the
    print_progress_start() function.
    Parameters
    ----------
    thread : threading.Thread
        THe thread handle returned by the print_progress_start() function.

    Returns
    -------
    None.

    """
    global stop_progress
    stop_progress = True
    thread.join()
    return


def print_msg(
    msg: str,
    colour: str = "",
    msg_type: str = "",
) -> None:
    """
    Author: Mitch Albert
    Prints a message to the terminal. The message is printed in the colour specified
    with the colour parameter. The msg_type parameter is printed before the message.
    This is used by the other print utility functions to print different types of
    messages with the same general format.

    Parameters
    ----------
    msg : str
        The message to print.
    colour : str, optional
        The colour to print the message in. The default is "".
    msg_type : str, optional
        The message type to print before the message. The default is "".

    Returns
    -------
    None

    """
    print(f"{BOLD}{colour}{msg_type}{RST}{colour}{msg}{RST}")
    return


def print_info(msg: str) -> None:
    """
    Author: Mitch Albert
    Prints an information message to the terminal. The message is printed
    in blue with the "INFO: " prefix.

    Parameters
    ----------
    msg : str
        The message to print.

    Returns
    -------
    None
    """
    print_msg(msg, OKBLUE, msg_type="INFO: ")
    return


def print_info_complete(msg: str) -> None:
    """
    Author: Mitch Albert
    Prints an information message to the terminal. The message is printed
    in green with the "INFO: " prefix. Used to indicate that a process has
    completed successfully.

    Parameters
    ----------
    msg : str
        The message to print.

    Returns
    -------
    None
    """
    print_msg(msg, OKGREEN, "INFO: ")
    return


def print_warning_msg(msg: str) -> None:
    """
    Author: Mitch Albert
    Prints a warning message to the terminal. The message is printed in yellow
    with the "WARNING: " prefix.

    Parameters
    ----------
    msg : str
        The message to print.

    Returns
    -------
    None
    """
    print_msg(msg, WARNING, "WARNING: ")
    return


def print_error_msg(msg: str) -> None:
    """
    Author: Mitch Albert
    Prints an error message to the terminal. The message is printed in red
    with the "ERROR: " prefix.

    Parameters
    ----------
    msg : str
        The message to print.

    Returns
    -------
    None

    """
    print_msg(msg, FAIL, "ERROR: ")
    return


def get_user_float(msg: str) -> float:
    """
    Author: Mitch Albert
    Gets a float from the user. If the user enters a non-float value, the
    function will continue to prompt the user until a valid float is entered.
    Parameters
    ----------
    msg : str
        DESCRIPTION.

    Returns
    -------
    float
        DESCRIPTION.

    """
    while True:
        try:
            return float(
                input(
                    f"""
    {msg}"""
                )
            )

        except ValueError:
            print_error_msg(msg_value_error_float)
            continue


def get_top_root() -> Tk:
    """
    Author: Mitch Albert
    Creates an invisible root window that has been forced to top and into focus.

    Returns
    -------
    Tk
        The invisible top level root window.
    """
    root = Tk()
    root.withdraw()
    root.overrideredirect(True)
    root.geometry("0x0+0+0")
    root.attributes("-alpha", 0)
    root.deiconify()
    root.lift()
    root.attributes("-topmost", True)
    root.after_idle(root.attributes, "-topmost", False)
    root.focus_force()
    return root


def load_files(
    files: list[str] | str, verbose: str = True
) -> list[gpd.GeoDataFrame] | gpd.GeoDataFrame:
    """
    Author: Mitch Albert
    Loads a list of files into a list of GeoDataFrames. If a single file name is
    passed that is not is a list, the function will return a single GeoDataFrame
    not inside a list. If a list of files is passed, even if it only contains
    1 file, the function will return a list.

    Parameters
    ----------
    files : list[str] | str
        The list of file names to load, or a single file name.
    verbose : str, optional
        Controls whether the function prints progress messages and file information.
        The default is True.

    Returns
    -------
    list[gpd.GeoDataFrame] | gpd.GeoDataFrame
        A list of geodataframes if a list was passed in or a single geodataframe
        if a single file name was passed in.
    """
    if verbose:
        print_info(f"Loading file(s)...")

    gdfs = []
    single_file = False

    if not isinstance(files, list):
        files = [files]
        single_file = True

    for file in files:
        try:
            if verbose:
                print_info(f"Loading {file}")
                progress = print_progress_start("Loading", dots=10, time=1)
            gdf = gpd.read_file(file)
            gdfs.append(gdf)
        except Exception as e:
            print_error_msg(f"Error loading file: {file}\n")
            print(e)
            continue
        finally:
            if verbose:
                print_progress_stop(progress)
                print_info_complete(f"Loading {file.split('/')[-1]} complete")
                print_info(f"CRS: {gdf.crs}")
                print_info(f"Shape: {gdf.shape[0]} Rows, {gdf.shape[1]} Columns\n")
                print_info("Columns: " + ", ".join(str(col) for col in gdf.columns))

    return gdfs[0] if single_file else gdfs


def get_file(
    f_types: tuple[str, str] | list[tuple[str, str]] = ft_standard,
    title: str = "Select File To Load",
    initialdir=getcwd(),
) -> str:
    """
    Author: Mitch Albert
    Opens a tkinter file dialog for a user to selelect a single file to load.
    Uses get_files() to do the heavy lifting, but passes the multi=False to limit
    the user to selecting a single file.

    Parameters
    ----------
    f_types : tuple[str, str] | list[tuple[str, str]], optional
        The file type(s) allowed. The default is standard_types.
    title : str, optional
        Title of the dialog box. Default is "Select File To Load".

    Returns
    -------
    str | None
        A str that is pathlike, or None if cancel is selected.
    """

    file = get_files(f_types, title=title, initialdir=initialdir, multi=False)

    return file[0] if file != None else None


def get_files(
    f_types: tuple[str, str] | list[tuple[str, str]] = ft_standard,
    title: str = "Select Files To Load",
    initialdir: str = getcwd(),
    multi: bool = True,
) -> List[str]:
    """
    Author: Mitch Albert
    Opens a tkinter file dialog for a user to selelect file(s) to load.

    Parameters
    ----------
    f_types : tuple[str, str] | list[tuple[str, str]], optional
        The file type(s) allowed. The default is standard_types.
    title : str, optional
        Title of dialog box. Default is "Select Files To Load".
    initialdir : str, optional
        The initial directory to open the dialog box in. The default is getcwd().
    mutli : bool, optional
        Whether or not to allow multiple file selection. The default is True.
    Returns
    -------
    List[str] | None
        A list of str's that is pathlike, or None if cancel is selected
    """

    if not isinstance(f_types, list):
        f_types = [f_types]

    root = get_top_root()
    files = tkinter.filedialog.askopenfilename(
        initialdir=initialdir,
        title=title,
        filetypes=f_types,
        multiple=multi,
        parent=root,
    )
    if not multi:
        files = (files,)
    root.destroy()
    return list(files) if len(files) else None


def get_files_from_dir(
    f_types: tuple[str, str] | list[tuple[str, str]] = ft_any,
    title: str = "Select Directory To Load Files From",
    initialdir: str = getcwd(),
) -> List[str]:
    """
    Author: Mitch Albert
    Opens a tkinter file dialog for a user to selelect a directory. All
    contained files matching the filter will be returned.

    Parameters
    ----------
    f_types : tuple[str, str] | list[tuple[str, str]], optional
        The file type(s) allowed. The default is ft_any.
    title : str, optional
        Title of the dialog box. Default is "Select Directory To Load Files
        From".
    initialdir : str, optional
        The initial directory to open the dialog box in. The default is getcwd().

    Returns
    -------
    List[str] | None
        A list of strings that are pathlike, or None if cancel is selected or
        no files
        are found that match the filter.
    """

    wd = getcwd()
    root = get_top_root()
    dir = tkinter.filedialog.askdirectory(
        title=title, initialdir=initialdir, mustexist=True, parent=root
    )
    root.destroy()
    files = []
    if dir != None:
        chdir(dir)
        if not isinstance(f_types, list):
            f_types = [f_types]
        for f in f_types:
            type_tup = f[1]
            if type(type_tup) is not tuple:
                type_tup = (type_tup,)
            for t in type_tup:
                f_list = glob(t)
                for file in f_list:
                    files.append(path.join(getcwd(), file))
    chdir(wd)

    return files if len(files) else None


def get_save_file_name(
    f_types: tuple[str, str] | list[tuple[str, str]] = ft_standard_save,
    title: str = "Save File",
    initialdir: str = getcwd(),
) -> str:
    """
    Author: Mitch Albert
    Open a tkinter file dialog for the user to indicate where and what to
    save a file as.

    Parameters
    ----------
    f_types : tuple[str, str] | list[tuple[str, str]], optional
        The file type(s) allowed. The default is standard_types.
    title : str, optional
        Title of dialog box. Default is "Save File".
    initialdir : str, optional
        The initial directory to open the dialog box in. The default is getcwd().

    Returns
    -------
    str | None
        A str that is pathlike, or None if cancel is selected.
    """
    if not isinstance(f_types, list):
        f_types = [f_types]
    root = get_top_root()
    file = tkinter.filedialog.asksaveasfilename(
        confirmoverwrite=True,
        initialdir=initialdir,
        title=title,
        defaultextension=ft_standard_save[0][1],
        filetypes=f_types,
        parent=root,
    )
    root.destroy()
    return file if len(file) else None


def get_user_selection(
    item_list: list[any],
    multi: bool = False,
    title: str = "Please Make A Selection",
    x: int = 400,
    y: int = 600,
    bg: str = "#5ea5c9",
) -> list[any]:
    """
    Author: Mitch Albert
    Opens a Tkinter window with the given list of items to select from.
    Selction can be single or multiple.

    Parameters
    ----------
    item_list : list[str]
        The list representing the items to select from.
    multi : bool, optional
        Determines whether multiple selections are allowed or not. The default
        is False.
    title : str, optional
        The title of the Tkinter window. The default is "Please Make A
        Selection".
    x : int, optional
        The width of the Tkinter window. The default is 400.
    y : int, optional
        The height of the Tkinter window. The default is 600.
    bg : str, optional
        The background color of the Tkinter window. The default is "#5ea5c9".

    Returns
    -------
    list[str]
        A list of selected items, or an empty list if none are selected or
        cancel is selected. If `multi` is False, the list can contain only
        one item.

    """
    multi = MULTIPLE if multi else SINGLE
    selected = []

    # internal function to get the selected items
    def getSelected():
        for i in lb.curselection():
            selected.append(lb.get(i))
        root.destroy()

    # create the window
    root = Tk()
    root.title(title)
    root.geometry(str(x) + "x" + str(y))
    root.config(bg=bg, pady=20, padx=20)

    # create frame for listbox and scrollbars
    frame = Frame(root)
    frame.pack()

    # pack horizontal scrollbar
    sbh = Scrollbar(frame, orient=HORIZONTAL)
    sbh.pack(side=BOTTOM, fill=X)

    # create listbox and pack it
    list_length = 25 if len(item_list) > 25 else len(item_list)
    lb = Listbox(frame, height=list_length, width=0, selectmode=multi, activestyle=NONE)
    lb.pack(side=LEFT)

    # pack vertical scrollbar
    sb = Scrollbar(frame, orient=VERTICAL)
    sb.pack(side=RIGHT, fill=Y)

    # configure listbox and scrollbar commands
    lb.configure(yscrollcommand=sb.set, xscrollcommand=sbh.set)
    sb.config(command=lb.yview)
    sbh.config(command=lb.xview)

    # add items to listbox
    index = 0
    for item in item_list:
        lb.insert(index, item)
        index += 1

    # add buttons
    Button(root, text="Finish", command=getSelected).pack(pady=20)
    Button(root, text="Cancel", command=root.quit).pack(pady=10)

    # make window appear on top of all other windows and run
    root.lift()
    root.attributes("-topmost", True)
    root.after_idle(root.attributes, "-topmost", False)
    root.mainloop()

    return selected
