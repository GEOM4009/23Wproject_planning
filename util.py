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

# import modules
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
    """Provide a progress indicator in the terminal. The progress indicator is a the
    msg string followed by a series of dots. The dots are printed at a rate of time
    seconds per dot. The number of dots is controlled by the dots parameter.
    Author: Mitch Albert

    :param msg: The msg string is printed before the dots, defaults to msg_processing.
    :type msg: str, optional
    :param dots: The number of dots to prints before resetting back to the message string, defaults to 10.
    :type dots: int, optional
    :param time: The time in seconds between each dot, defaults to 1
    :type time: float, optional
    :return: The progress thread handle. This is required to stop the progress indicator.
    :rtype: threading.Thread
    """

    def back(spaces: int) -> str:
        """Utility function to move the cursor back a number of spaces. This is used to
        remove the dots printed by the progress indicator.
        Author: Mitch Albert

        :param spaces: The number of spaces to move the cursor back.
        :type spaces: int
        :return: The character string to move the cursor back 'spaces' spaces.
        :rtype: str
        """
        return f"\x1b[{spaces}D"

    def progress_thread(msg: str, dots: int, time: float):
        """Internal thread function to print the progress dots while the work is being done.
        Author: Mitch Albert
        :param msg: The msg string is printed before the dots.
        :type msg: str
        :param dots: The number of dots to prints before resetting back to the message string.
        :type dots: int
        :param time: The time in seconds between each dot.
        :type time: float
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
    """Stop the progress indicator thread, using the thread handle returned by
    :func:`~print_progress_start`.
    Author: Mitch Albert

    :param thread: The thread handle returned by the :func:`~print_progress_start` function.
    :type thread: threading.Thread
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
    """Print a message to the terminal. The message is printed in the colour specified
    with the colour parameter. The msg_type parameter is printed before the message.
    This is used by the other print utility functions to print different types of
    messages with the same general format.
    Author: Mitch Albert

    :param msg: The message to print.
    :type msg: str
    :param colour: The colour to print the message in, defaults to "".
    :type colour: str, optional
    :param msg_type: The message type to print before the message, defaults to "".
    :type msg_type: str, optional
    """
    print(f"{BOLD}{colour}{msg_type}{RST}{colour}{msg}{RST}")
    return


def print_info(msg: str) -> None:
    """Print an information message to the terminal. The message is printed
    in blue with the "INFO: " prefix.
    Author: Mitch Albert
    :param msg: The message to print.
    :type msg: str
    """
    print_msg(msg, OKBLUE, msg_type="INFO: ")
    return


def print_info_complete(msg: str) -> None:
    """Print an information message to the terminal. The message is printed
    in green with the "INFO: " prefix. Used to indicate that a process has
    completed successfully.
    Author: Mitch Albert

    :param msg: The message to print.
    :type msg: str
    """
    print_msg(msg, OKGREEN, "INFO: ")
    return


def print_warning_msg(msg: str) -> None:
    """Print a warning message to the terminal. The message is printed in yellow
    with the "WARNING: " prefix.
    Author: Mitch Albert

    :param msg: _description_
    :type msg: The message to print.
    """
    print_msg(msg, WARNING, "WARNING: ")
    return


def print_error_msg(msg: str) -> None:
    """Print an error message to the terminal. The message is printed in red
    with the "ERROR: " prefix.
    Author: Mitch Albert

    :param msg: The message to print.
    :type msg: str
    """
    print_msg(msg, FAIL, "ERROR: ")
    return


def get_user_float(msg: str) -> float:
    """Get a float from the user. If the user enters a non-float value, the
    function will continue to prompt the user until a valid float is entered.
    Author: Mitch Albert

    :param msg: The message to display to the user.
    :type msg: str
    :return: The user's input as a float.
    :rtype: float
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
    """Create an invisible root window that has been forced to top and into focus.
    Author: Mitch Albert

    :return: The invisible top level root window.
    :rtype: Tk
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
    """Load a list of files into a list of GeoDataFrames. If a single file name is
    passed that is not is a list, the function will return a single GeoDataFrame
    not inside a list. If a list of files is passed, even if it only contains
    1 file, the function will return a list.
    Author: Mitch Albert

    :param files: The list of file names to load, or a single file name.
    :type files: list[str] | str
    :param verbose: Controls whether the function prints progress messages and file information, defaults to True.
    :type verbose: str, optional
    :return: A list of geodataframes if a list was passed in or a single geodataframe
            if a single file name was passed in.
    :rtype: list[gpd.GeoDataFrame] | gpd.GeoDataFrame
    """
    if verbose:
        print_info("Loading file(s)...")

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
            gdf.name = file.split("/")[-1]
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
                print_info(f"Shape: {gdf.shape[0]} Rows, {gdf.shape[1]} Columns")
                print_info("Columns: " + ", ".join(str(col) for col in gdf.columns))

    return gdfs[0] if single_file else gdfs


def get_file(
    f_types: tuple[str, str] | list[tuple[str, str]] = ft_standard,
    title: str = "Select File To Load",
    initialdir=getcwd(),
) -> str:
    """Open a tkinter file dialog for a user to selelect a single file to load.
    Uses get_files() to do the heavy lifting, but passes the multi=False to limit
    the user to selecting a single file.
    Author: Mitch Albert

    :param f_types: The file type(s) allowed, defaults to ft_standard.
    :type f_types: tuple[str, str] | list[tuple[str, str]], optional
    :param title: Title of the dialog box, defaults to "Select File To Load"
    :type title: str, optional
    :param initialdir: The directory the window will open to, defaults to getcwd().
    :type initialdir: str, optional
    :return: A str that is pathlike, or None if cancel is selected.
    :rtype: str
    """
    file = get_files(f_types, title=title, initialdir=initialdir, multi=False)
    return file[0] if file != None else None


def get_files(
    f_types: tuple[str, str] | list[tuple[str, str]] = ft_standard,
    title: str = "Select Files To Load",
    initialdir: str = getcwd(),
    multi: bool = True,
) -> List[str]:
    """Open a tkinter file dialog for a user to selelect file(s) to load.
    Author: Mitch Albert

    :param f_types: The file type(s) allowed, defaults to ft_standard.
    :type f_types: tuple[str, str] | list[tuple[str, str]], optional
    :param title: Title of dialog box, defaults to "Select Files To Load"
    :type title: str, optional
    :param initialdir: The initial directory dialog box open to, defaults to getcwd().
    :type initialdir: str, optional
    :param multi: Enables or disables multiple file selection, defaults to True.
    :type multi: bool, optional
    :return: A list of str's that is pathlike, or None if cancel is selected.
    :rtype: List[str]
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
    """Open a tkinter file dialog for a user to selelect a directory. All
    contained files matching the filter will be returned.
    Author: Mitch Albert

    :param f_types: The file type(s) allowed, defaults to ft_any.
    :type f_types: tuple[str, str] | list[tuple[str, str]], optional
    :param title: Title of the dialog box, defaults to "Select Directory To Load Files From".
    :type title: str, optional
    :param initialdir: The initial directory to open the dialog box in, defaults to getcwd().
    :type initialdir: str, optional
    :return: A list of strings that are pathlike, or None if cancel is selected or
             no files are found that match the filter.
    :rtype: List[str]
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
    """Open a tkinter file dialog for the user to indicate where and what to
    save a file as.
    Author: Mitch Albert

    :param f_types: The file type(s) allowed, defaults to ft_standard_save.
    :type f_types: tuple[str, str] | list[tuple[str, str]], optional
    :param title: Title of dialog box, defaults to "Save File".
    :type title: str, optional
    :param initialdir:  The initial directory dialog box open to, defaults to getcwd()
    :type initialdir: str, optional
    :return: A str that is pathlike, or None if cancel is selected.
    :rtype: str
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
    """Open a Tkinter window with the given list of items to select from.
    Selction can be single or multiple.
    Author: Mitch Albert

    :param item_list: The list representing the items to select from.
    :type item_list: list[any]
    :param multi: Determines whether multiple selections are allowed or not, defaults to False.
    :type multi: bool, optional
    :param title: The title of the Tkinter window, defaults to "Please Make A Selection".
    :type title: str, optional
    :param x: The width of the Tkinter window, defaults to 400
    :type x: int, optional
    :param y: The height of the Tkinter window, defaults to 600
    :type y: int, optional
    :param bg: The background color of the Tkinter window, defaults to "#5ea5c9"
    :type bg: str, optional
    :return: A list of selected items, or an empty list if none are selected. If `multi` is False,
             the list can contain only one item.
    :rtype: list[any]
    """
    # set the selection mode
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

    # make window appear on top of all other windows and run
    root.lift()
    root.attributes("-topmost", True)
    root.after_idle(root.attributes, "-topmost", False)
    root.mainloop()

    return selected
