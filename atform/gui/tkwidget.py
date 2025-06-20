import tkinter as tk
import tkinter.ttk as ttk


def new(cls, *args, **kwargs):
    instance = object.__new__(cls)
    cls._instances.append(instance)
    return instance


def make_cls(cls):
    """ """
    return type(cls.__name__, (cls,), {"__new__": new, "_instances": []})


Button = make_cls(tk.Button)
Frame = make_cls(tk.Frame)
IntVar = make_cls(tk.IntVar)
Label = make_cls(tk.Label)
Scrollbar = make_cls(tk.Scrollbar)
ScrolledText = make_cls(tk.scrolledtext.ScrolledText)
StringVar = make_cls(tk.StringVar)
Tk = make_cls(tk.Tk)

LabelFrame = make_cls(ttk.LabelFrame)
Notebook = make_cls(ttk.Notebook)
Treeview = make_cls(ttk.Treeview)
