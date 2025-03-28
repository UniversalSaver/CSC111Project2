"""
Module Description
==================
A file with functions for creating the window which the user will use. Uses tkinter.
The buttons make calls to functions in graph_processing.py.

Copyright and Usage Information
===============================
This file is solely provided for the use in grading and review of the named student's
work by the TAs and Professors of CSC111. All further distribution of this code whether
as is or modified is firmly prohibited.

This file is Copyright (c) Nabhan Rashid, Danny Tran, and Tai Poole
"""
import time
from tkinter.font import Font
from tkinter import Tk, Frame, Label, Button, OptionMenu, Text, StringVar, Entry
import tkinter as tk
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import graph_processing as gp


class Memory():
    '''
    A class to represent the memory of the program.
    Contains a collection of pointers to dynamic widgets. Wrapper class.

    Instance Attributes:
        dbg: text widget for the dbg frame
        graph: label widget for the graph frame
        canvas: canvas widget for the graph frame
        fig: figure widget for the graph frame
    '''
    dbg: Text | None
    graph: Label | None
    canvas: FigureCanvasTkAgg | None
    fig: Figure | None

    def __init__(self) -> None:
        self.dbg = None
        self.graph = None
        self.canvas = None
        self.fig = None

class App():
    '''
    A class to represent the GUI for the user to interact with the program.

    Instance Attributes:
        root: the main window of the application
        font: the font to be used in the application
        dimensions: the dimensions of the window (found during init, depend on screen size)
        names: a list of 2 items that hold the names of the actors to be searched
        filters: a list of items that hold the filters to be applied to the search
        db_path: the path to the database file
        mem: memory object, holds important widgets
    '''
    root: Tk
    font: Font
    dimensions: tuple[int, int]
    names: list[StringVar]
    filters: list[StringVar]
    db_path: str
    mem: Memory

    def __init__(self, path: str) -> None:
        self.root = Tk()
        self.root.title("Created by Tai Poole, Nabhan Rashid, and Danny Tran")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.dimensions = (int(screen_width / 4 * 3), int(screen_height / 4 * 3))
        center_x = int(screen_width / 2 - self.dimensions[0] / 2)
        center_y = int(screen_height / 2 - self.dimensions[1] / 2)
        self.root.geometry(f'{self.dimensions[0]}x{self.dimensions[1]}+{center_x}+{center_y}')
        self.font = Font(family="Apple Symbols", size=15)  # shouldve been comic sans -T
        self.db_path = path
        self.names = []
        self.filters = []

        self.init_input(self.root)
        self.init_display(self.root)

        self.figure = Figure(figsize=(20, 20), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.graph_window)

    def run(self) -> None:
        '''
        Runs the application
        '''
        self.root.mainloop()

    def init_input(self, main_frame: Tk) -> None:
        '''
        Initializes the input frame (left side of the window)
        '''
        input_frame = Frame(main_frame, bg="#dee2e6", relief='raised', bd=15, width=self.dimensions[0] / 3)

        self.init_info(input_frame)
        self.init_field(input_frame)

        input_frame.pack(side=tk.LEFT, fill=tk.BOTH)
        input_frame.pack_propagate(False)

    def init_info(self, input_frame: Frame) -> None:
        '''
        Initializes the info frame (top left side of the window)
        '''
        info_frame = Frame(input_frame, bg="#adb5bd", bd=15)
        title = Label(info_frame, font=self.font, bg="#adb5bd", fg="#343a40", wraplength=(self.dimensions[0] / 3) - 70, justify=tk.CENTER,
                          text="The really cool connected thing TODO NAME")
        description = Label(info_frame, font=self.font, bg="#adb5bd", fg="#343a40", wraplength=(self.dimensions[0] / 3) - 70, justify=tk.CENTER,
                                text="This is a really cool thing that will connect actors to movies. she kevin on my bacon till i 6 degrees or less")
        info_frame.pack(side=tk.TOP, fill=tk.BOTH)
        title.pack(side=tk.TOP)
        description.pack(side=tk.TOP)

    def init_field(self, input_frame: Frame) -> None:
        '''
        Initializes the field frame (bottom left side of the window)
        '''
        field_frame = Frame(input_frame, bd=15, bg="#ced4da")

        self.init_name1(field_frame)
        self.init_name2(field_frame)
        self.init_search(field_frame)

        field_frame.pack(fill=tk.BOTH, expand=True)

    def init_name1(self, field_frame: Frame) -> None:
        '''
        Initializes the first name input frame
        '''
        name1_frame = Frame(field_frame, bd=15, bg="#ced4da")
        name1_label = Label(name1_frame, bg="#ced4da", fg="#495057", font=self.font, text="Starting actor's name: ")
        self.names.append(StringVar(self.root))
        name1_input = Entry(name1_frame, textvariable=self.names[0])

        name1_frame.pack(expand=True)
        name1_label.pack()
        name1_input.pack()

    def init_name2(self, field_frame: Frame) -> None:
        '''
        Initializes the second name input frame
        '''
        name2_frame = Frame(field_frame, bd=15, bg="#ced4da")
        name2_label = Label(name2_frame, bg="#ced4da", fg ="#495057", font=self.font, text="Ending actor's name: ")
        self.names.append(StringVar(self.root))
        name2_input = Entry(name2_frame, textvariable=self.names[1])

        name2_frame.pack(expand=True)
        name2_label.pack()
        name2_input.pack()

    def init_search(self, field_frame: Frame) -> None:
        '''
        Initializes the search input frame, including search type and search button
        '''
        search_frame = Frame(field_frame, bd=15, bg="#ced4da")
        search_button = Button(search_frame, bg="#ced4da", bd=0, command=self.doTheThing, font=self.font, text="Go!")

        self.init_filter_dropdown(search_frame)
        self.init_filter_input(search_frame)

        search_frame.pack(expand=True)
        search_button.pack(side=tk.RIGHT)

    def init_filter_dropdown(self, search_frame: Frame) -> None:
        '''
        Initializes the first filter input frame
        '''
        filter1_frame = Frame(search_frame, bd=15, bg="#ced4da")
        filter1_label = Label(filter1_frame, bg="#ced4da", fg="#495057", font=self.font, text="Living status: ")
        filter1 = StringVar(self.root)
        filter1.set(" ")
        self.filters.append(filter1)
        type_box = OptionMenu(filter1_frame, self.filters[0], "Any", "Alive", "Deceased")
        type_box.config(bg="#ced4da", fg="#495057")

        filter1_frame.pack(expand=True)
        filter1_label.pack()
        type_box.pack()

    def init_filter_input(self, search_frame: Frame) -> None:
        '''
        Initializes the first filter input frame
        '''
        filter2_frame = Frame(search_frame, bd=15, bg="#ced4da")
        filter2_label = Label(filter2_frame, bg="#ced4da", fg="#495057", font=self.font, text="Released After: ")
        filter2 = StringVar(self.root)
        filter2.set(" ")
        self.filters.append(filter2)
        input_box = Entry(filter2_frame, textvariable=self.filters[0], fg="#495057")

        filter2_frame.pack(expand=True)
        filter2_label.pack()
        input_box.pack()

    def init_display(self, main_frame: Tk) -> None:
        '''
        Initializes the display frame (right side of window)
        '''
        display_frame = Frame(main_frame, bg="#f8f9fa", bd=15)
        self.init_graph(display_frame)
        self.init_dbg(display_frame)

        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def init_dbg(self, display_frame: Frame) -> None:
        '''
        Initializes the debug frame, for displaying the status of the search
        '''
        dbg_frame = Frame(display_frame, bg="#adb5bd", bd=15, height=self.dimensions[1] * 1 / 9, width=self.dimensions[0] * 2 / 3)
        self.status_window = Text(dbg_frame, font=self.font)
        self.status_window.insert(tk.END, "")
        self.status_window.config(state=tk.DISABLED)

        dbg_frame.pack(side=tk.BOTTOM)
        self.status_window.pack(fill=tk.BOTH, expand=True)
        dbg_frame.pack_propagate(False)

    def init_graph(self, display_frame: Frame) -> None:
        '''
        Initializes the graph frame (top right side of the window)
        '''
        graph_frame = Frame(display_frame, bg="#f8f9fa")
        self.graph_window = Label(graph_frame, fg="#495057", bg="#f8f9fa", font=self.font, text="Graph goes here")
        self.graph_window.pack(expand=True)

        graph_frame.pack(side=tk.TOP, expand=True)
        self.graph_window.pack(fill=tk.BOTH, expand=True)

    def doTheThing(self) -> None:
        name1, name2 = self.names[0].get(), self.names[1].get()
        search_type = self.type.get()
        self.status_window.config(state=tk.NORMAL)
        self.status_window.delete('1.0', tk.END)
        self.status_window.insert(tk.END, "Searching...")
        self.status_window.config(state=tk.DISABLED)
        g = gp.ShortestActorGraph(self.db_path)

        start_time = time.time()
        id1, id2 = g.get_actor_id(name1), g.get_actor_id(name2)
        if id1 != "" and id2 != "":
            path = g.get_path(id1, id2) #change for connection type?
            if len(path) > 0:
                info = g.make_networkx_graph(path)
                wait = round(time.time() - start_time, 3)

                self.status_window.config(state=tk.NORMAL)
                self.status_window.delete('1.0', tk.END)
                d = int((len(path) - 1) / 2)
                p = "s" if d != 1 else ""
                msg = f"Found {search_type} connection in {wait} seconds and {d} degree{p} of seperation"
                self.status_window.insert(tk.END, msg)
                self.status_window.config(state=tk.DISABLED)
                self.render(info)
            else:
                self.status_window.config(state=tk.NORMAL)
                self.status_window.delete('1.0', tk.END)
                self.status_window.insert(tk.END, "No connection found :(")
                self.status_window.config(state=tk.DISABLED)
        else:
            self.status_window.config(state=tk.NORMAL)
            self.status_window.delete('1.0', tk.END)
            self.status_window.insert(tk.END,
                                      f"Sorry, actor {name1 if id1 == "" else name2 if id2 == "" else ""} not found")
            self.status_window.config(state=tk.DISABLED)

    def render(self, info: nx.Graph) -> None:
        '''
        Renders the graph
        '''
        # DO NOT TOUCH ANYTHING IT HAS DRIVEN ME MAD ON THE ROCKS
        self.canvas.get_tk_widget().pack_forget()
        plt.close(self.figure)
        graph_w, graph_h = self.dimensions[0] * 2 / 3 - 30, self.dimensions[1] * 8 / 9 - 30
        self.figure = Figure(figsize=(graph_w / 100, graph_h / 100), dpi=100)
        plot = self.figure.add_axes((0, 0, 1, 1))
        plot.axis('off')
        pos = nx.kamada_kawai_layout(info)
        colours = [info.nodes[k]['color'] for k in info.nodes]
        nx.draw(info, pos, node_color=colours, ax=plot, with_labels=True, font_size=8)
        x_min, x_max = plot.get_xlim()
        y_min, y_max = plot.get_ylim()
        x_span = x_max - x_min
        y_span = y_max - y_min
        padding = 0.05 * max(x_span, y_span)
        plot.set_xlim(x_min - padding, x_max + padding)
        plot.set_ylim(y_min - padding, y_max + padding)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.graph_window)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()


if __name__ == "__main__":
    import python_ta

    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['E1136'],
    #     'extra-imports': ['csv', 'networkx', 'sqlite3', 'collections', 'matplotlib.pyplot'],
    #     'allowed-io': ['load_review_graph'],
    #     'max-nested-blocks': 4
    # })
    app = App("./data_files/basically_all.db")
    app.run()
