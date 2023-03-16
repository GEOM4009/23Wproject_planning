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
"""


from os import getcwd, chdir, path
import tkinter.filedialog
from tkinter import Tk, Frame, Listbox, Scrollbar, Button
from tkinter.constants import *
from typing import List
from glob import glob
from defs import *



def print_error_msg(msg) -> None:
    print(f"{RED}{msg}{RST}")
    return


def get_user_float(msg: str) -> float:
    while True:
        try:
            return float(
                input(
    f"""
    {msg}"""
                )
            )

        except ValueError:
            print_error_msg(msg_value_error)
            continue

def get_top_root() -> Tk:
    """
    Creates an invisible root window that has been forced to top and into focus.

    Returns
    -------
    Tk
        The invisible top level root window.
    """
    root = Tk()
    root.withdraw()
    root.overrideredirect(True)
    root.geometry('0x0+0+0')
    root.attributes('-alpha', 0)
    root.deiconify()
    root.lift()
    root.attributes("-topmost", True)
    root.after_idle(root.attributes, "-topmost", False)
    root.focus_force()
    return root

def get_file(
    f_types: tuple[str, str] | list[tuple[str, str]] = ft_standard,
    title: str = "Select File To Load",
    initialdir=getcwd(),
) -> str:
    """
    Opens a tkinter file dialog for a user to selelect a single file to load.

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
    initialdir=getcwd(),
    multi: bool = True,
) -> List[str]:
    """
    Opens a tkinter file dialog for a user to selelect file(s) to load.

    Parameters
    ----------
    f_types : tuple[str, str] | list[tuple[str, str]], optional
        The file type(s) allowed. The default is standard_types.
    title : str, optional
        Title of dialog box. Default is "Select Files To Load".

    Returns
    -------
    List[str] | None
        A list of str's that is pathlike, or None if cancel is selected
    """

    if not isinstance(f_types, list):
        f_types = [f_types]

    root = get_top_root()
    files = tkinter.filedialog.askopenfilename(
        initialdir=initialdir, title=title, filetypes=f_types, multiple=multi, parent=root
    )
    root.destroy()
    return [files] if len(files) else None


def get_files_from_dir(
    f_types: tuple[str, str] | list[tuple[str, str]] = ft_any,
    title: str = "Select Directory To Load Files From",
    initialdir=getcwd(),
) -> List[str]:
    """
    Opens a tkinter file dialog for a user to selelect a directory. All
    contained files matching the filter will be returned.

    Parameters
    ----------
    f_types : tuple[str, str] | list[tuple[str, str]], optional
        The file type(s) allowed. The default is ft_any.
    title : str, optional
        Title of the dialog box. Default is "Select Directory To Load Files
        From".

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
    initialdir=getcwd(),
) -> str:
    """
    Open a tkinter file dialog for the user to indicate where and what to
    save a file as.

    Parameters
    ----------
    f_types : tuple[str, str] | list[tuple[str, str]], optional
        The file type(s) allowed. The default is standard_types.
    title : str, optional
        Title of dialog box. Default is "Save File".

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
        parent=root
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
    Opens a Tkinter window with the given list of items to select from.
    Selction can be single or multiple.

    Parameters
    ----------
    item_list : list[str]
        The list of strings representing the items to select from.
    multi : bool, optional
        Determines whether multiple selections are allowed or not. The default
        is False.
    title : str, optional
        The title of the Tkinter window. The default is "Please Make A
        Selection".

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
