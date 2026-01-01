"""
This module provides a set of wrapper classes around tkinter widgets to
mitigate errors during unit tests that seem to be the result of garbage
collecting tkinter widgets while the mainloop is not running, which it never
does during normal unit tests. The errors this is intended to address are:

    RuntimeError: main thread is not in main loop
    Tcl_AsyncDelete: async handler deleted by the wrong thread

Wrapper classes maintain an internal reference to all instances, thereby
preventing garbage collection, and should otherwise have no effect.
"""

import tkinter as tk
from tkinter import scrolledtext, ttk


def new(cls, *_args, **_kwargs):
    """Assigned as the __new__ method to each wrapper class."""
    instance = object.__new__(cls)
    cls.instances.append(instance)
    return instance


def add_instance_storage(cls):
    """Wrapper class decorator to add instance storage attributes."""
    setattr(cls, "__new__", new)
    setattr(cls, "instances", [])
    return cls


# pylint: disable=missing-class-docstring
# pylint: disable=too-many-ancestors


@add_instance_storage
class BooleanVar(tk.BooleanVar):
    pass


@add_instance_storage
class Button(ttk.Button):
    pass


@add_instance_storage
class Checkbutton(ttk.Checkbutton):
    pass


@add_instance_storage
class Entry(ttk.Entry):
    pass


@add_instance_storage
class Frame(ttk.Frame):
    pass


@add_instance_storage
class IntVar(tk.IntVar):
    pass


@add_instance_storage
class Label(ttk.Label):
    pass


@add_instance_storage
class Radiobutton(ttk.Radiobutton):
    pass


@add_instance_storage
class Scrollbar(ttk.Scrollbar):
    pass


@add_instance_storage
class ScrolledText(scrolledtext.ScrolledText):
    pass


@add_instance_storage
class Spinbox(ttk.Spinbox):
    pass


@add_instance_storage
class StringVar(tk.StringVar):
    pass


@add_instance_storage
class Tk(tk.Tk):
    pass


@add_instance_storage
class LabelFrame(ttk.LabelFrame):
    pass


@add_instance_storage
class Notebook(ttk.Notebook):
    pass


@add_instance_storage
class Treeview(ttk.Treeview):
    pass


@add_instance_storage
class Separator(ttk.Separator):
    pass
