"""
A file with functions for creating the window which the user will use. Will use tkinter. The buttons will make calls
to functions in graph_processing.py

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
    """
    A class to represent the memory of the program.
    Contains a collection of pointers to dynamic widgets. Wrapper class.

    Instance Attributes:
        dbg: text widget for the dbg frame
        graph: label widget for the graph frame
        canvas: canvas widget for the graph frame
        fig: figure widget for the graph frame
        g: the graph object. here for storage :)
    """
    dbg: Text
    graph: Label
    canvas: FigureCanvasTkAgg
    fig: Figure
    g: gp.ShortestActorGraph

    def __init__(self, data: tuple[Text, Label, FigureCanvasTkAgg, Figure, gp.ShortestActorGraph]) -> None:
        self.dbg = data[0]
        self.graph = data[1]
        self.canvas = data[2]
        self.fig = data[3]
        self.g = data[4]


class App():
    """
    A class to represent the GUI for the user to interact with the program.

    Instance Attributes:
        root: the main window of the application
        font: the font to be used in the application
        dimensions: the dimensions of the window (found during init, depend on screen size)
        names: a list of 2 items that hold the names of the actors to be searched
        filters: a list of items that hold the filters to be applied to the search
        db_path: the path to the database file
        mem: memory object, holds important widgets
    """
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
        (dbg, graph) = self.init_display(self.root)

        fig = Figure(figsize=(20, 20), dpi=100)
        canvas = FigureCanvasTkAgg(fig, master=graph)
        g = gp.ShortestActorGraph(self.db_path)
        self.mem = Memory((dbg, graph, canvas, fig, g))

    def run(self) -> None:
        """
        Runs the application
        """
        self.root.mainloop()

    def init_input(self, main_frame: Tk) -> None:
        """
        Initializes the input frame (left side of the window)
        """
        input_frame = Frame(main_frame, bg="#dee2e6", relief='raised', bd=15, width=self.dimensions[0] / 3)

        self.init_info(input_frame)
        self.init_field(input_frame)

        input_frame.pack(side=tk.LEFT, fill=tk.BOTH)
        input_frame.pack_propagate(False)

    def init_info(self, input_frame: Frame) -> None:
        """
        Initializes the info frame (top left side of the window)
        """
        info_frame = Frame(input_frame, bg="#adb5bd", bd=15)
        title = Label(info_frame, font=self.font, bg="#adb5bd", fg="#343a40", wraplength=(self.dimensions[0] / 3) - 60,
                      justify=tk.CENTER, text=str("Welcome to the Hollywood connection finder"
                      "\n(or the Baconator if Wendy's allowed it)!\n"))
        description = Label(info_frame, font=self.font, bg="#adb5bd", fg="#343a40",
                            wraplength=(self.dimensions[0] / 3) - 60, justify=tk.CENTER,
                            text="Input two actor names from IMDB (as well as other restrictions), "
                            "and we will try to connect them "
                            "through mutual actors/movies.")
        info_frame.pack(side=tk.TOP, fill=tk.BOTH)
        title.pack(side=tk.TOP)
        description.pack(side=tk.TOP)

    def init_field(self, input_frame: Frame) -> None:
        """
        Initializes the field frame (bottom left side of the window)
        """
        field_frame = Frame(input_frame, bd=15, bg="#ced4da")
        search_button = Button(input_frame, bg="#ced4da", bd=0,
                               command=self.find_connection, font=self.font, text="Go!")

        self.init_name1(field_frame)
        self.init_name2(field_frame)
        self.init_filters(field_frame)

        search_button.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH)
        field_frame.pack(fill=tk.BOTH, expand=True)

    def init_name1(self, field_frame: Frame) -> None:
        """
        Initializes the first name input frame
        """
        name1_frame = Frame(field_frame, bd=15, bg="#ced4da")
        name1_label = Label(name1_frame, bg="#ced4da", fg="#495057", font=self.font, text="Starting actor's name: ")
        self.names.append(StringVar(self.root))
        name1_input = Entry(name1_frame, textvariable=self.names[0])

        name1_frame.pack(expand=True)
        name1_label.pack()
        name1_input.pack()

    def init_name2(self, field_frame: Frame) -> None:
        """
        Initializes the second name input frame
        """
        name2_frame = Frame(field_frame, bd=15, bg="#ced4da")
        name2_label = Label(name2_frame, bg="#ced4da", fg="#495057", font=self.font, text="Ending actor's name: ")
        self.names.append(StringVar(self.root))
        name2_input = Entry(name2_frame, textvariable=self.names[1])

        name2_frame.pack(expand=True)
        name2_label.pack()
        name2_input.pack()

    def init_filters(self, field_frame: Frame) -> None:
        """
        Initializes the search input frame, including search type and search button
        """
        search_frame = Frame(field_frame, bd=15, bg="#ced4da")
        search_label = Label(search_frame, bg="#ced4da", fg="#495057", font=self.font, text="Additional filters: ")

        search_label.pack(side=tk.TOP)

        self.init_filter_dropdown(search_frame)
        self.init_filter_input(search_frame)
        search_frame.pack(expand=True)

    def init_filter_dropdown(self, search_frame: Frame) -> None:
        """
        Initializes the first filter input frame
        """
        filter1_frame = Frame(search_frame, bd=15, bg="#ced4da")
        filter1_label = Label(filter1_frame, bg="#ced4da", fg="#495057", font=self.font, text="Living status: ")
        filter1 = StringVar(self.root)
        filter1.set("Any")
        self.filters.append(filter1)
        type_box = OptionMenu(filter1_frame, self.filters[0], "Any", "Alive", "Deceased")
        type_box.config(bg="#ced4da", fg="#495057")

        filter1_frame.pack(side=tk.LEFT, expand=True)
        filter1_label.pack()
        type_box.pack(expand=True, fill=tk.BOTH)

    def init_filter_input(self, search_frame: Frame) -> None:
        """
        Initializes the first filter input frame
        """
        filter2_frame = Frame(search_frame, bd=15, bg="#ced4da")
        filter2_label = Label(filter2_frame, bg="#ced4da", fg="#495057", font=self.font, text="Released After: ")
        filter2 = StringVar(self.root)
        filter2.set("0")
        self.filters.append(filter2)
        input_box = Entry(filter2_frame, textvariable=self.filters[1])

        filter2_frame.pack(side=tk.RIGHT, expand=True)
        filter2_label.pack()
        input_box.pack()

    def init_display(self, main_frame: Tk) -> tuple[Text, Label]:
        """
        Initializes the display frame (right side of window)
        """
        display_frame = Frame(main_frame, bg="#f8f9fa", bd=15)
        graph = self.init_graph(display_frame)
        dbg = self.init_dbg(display_frame)

        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        return (dbg, graph)

    def init_dbg(self, display_frame: Frame) -> Text:
        """
        Initializes the debug frame, for displaying the status of the search
        """
        dbg_frame = Frame(display_frame, bg="#adb5bd", bd=15,
                          height=self.dimensions[1] * 1 / 11, width=self.dimensions[0] * 2 / 3)
        dbg = Text(dbg_frame, font=self.font)
        dbg.insert(tk.END, "")
        dbg.config(state=tk.DISABLED)

        dbg_frame.pack(side=tk.BOTTOM)
        dbg.pack(fill=tk.BOTH, expand=True)
        dbg_frame.pack_propagate(False)

        return dbg

    def init_graph(self, display_frame: Frame) -> Label:
        """
        Initializes the graph frame (top right side of the window)
        """
        graph_frame = Frame(display_frame, bg="#f8f9fa")
        graph = Label(graph_frame, fg="#495057", bg="#f8f9fa", font=self.font, text="Graph goes here")
        graph.pack(expand=True)

        graph_frame.pack(side=tk.TOP, expand=True)
        graph.pack(fill=tk.BOTH, expand=True)

        return graph

    def find_connection(self) -> None:
        """
        Finds the connection between two actors, and displays it on the graph window.
        Uses graph_processing for the backend
        """
        name1, name2 = self.names[0].get(), self.names[1].get()
        is_alive, released_after = self.filters[0].get(), self.filters[1].get()
        try:
            released_after = int(released_after)
        except ValueError:
            released_after = 0
        self.mem.dbg.config(state=tk.NORMAL)
        self.mem.dbg.delete('1.0', tk.END)
        self.mem.dbg.insert(tk.END, "Searching...")
        self.mem.dbg.config(state=tk.DISABLED)
        self.mem.dbg.update()
        id1, id2 = self.mem.g.get_actor_id(name1), self.mem.g.get_actor_id(name2)
        start_time = time.time()
        if id1[0:2] == "nm" and id2[0:2] == "nm":
            # I'd like to note that 1888 is the oldest "movie" in the processed data set. Though it's a book?
            if is_alive == 'Any' and released_after < 1888:
                path = self.mem.g.get_path(id1, id2)
            else:
                path = self.mem.g.get_restricted_path(id1, id2, is_alive, released_after=released_after)
            if len(path) > 0:
                info = self.mem.g.make_networkx_graph(path)
                wait = round(time.time() - start_time, 3)

                self.mem.dbg.config(state=tk.NORMAL)
                self.mem.dbg.delete('1.0', tk.END)
                d = int((len(path) - 1) / 2)
                p = "s" if d != 1 else ""
                msg = f"Found a connection in {wait} seconds and {d} degree{p} of seperation"
                self.mem.dbg.insert(tk.END, msg)
                self.mem.dbg.config(state=tk.DISABLED)
                self.render(info)
            else:
                self.mem.dbg.config(state=tk.NORMAL)
                self.mem.dbg.delete('1.0', tk.END)
                self.mem.dbg.insert(tk.END, "No connection found :(")
                self.mem.dbg.config(state=tk.DISABLED)
        else:
            self.mem.dbg.config(state=tk.NORMAL)
            self.mem.dbg.delete('1.0', tk.END)
            if id1 == "tm":
                self.mem.dbg.insert(tk.END, f"Sorry, there are too many actors named {name1} ")
            elif id2 == "tm":
                self.mem.dbg.insert(tk.END, f"Sorry, there are too many actors named {name2}")
            else:
                self.mem.dbg.insert(tk.END,
                                    f"Sorry, actor {name1 if id1 == "" else name2 if id2 == "" else ""} not found")
            self.mem.dbg.config(state=tk.DISABLED)

    def render(self, info: nx.Graph) -> None:
        """
        Renders the graph
        """
        # DO NOT TOUCH ANYTHING IT HAS DRIVEN ME MAD ON THE ROCKS
        self.mem.canvas.get_tk_widget().pack_forget()
        plt.close(self.mem.fig)
        graph_w, graph_h = self.dimensions[0] * 2 / 3 - 30, self.dimensions[1] * 10 / 11 - 30
        self.mem.fig = Figure(figsize=(graph_w / 100, graph_h / 100), dpi=100)
        plot = self.mem.fig.add_axes((0, 0, 1, 1))
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
        self.mem.canvas = FigureCanvasTkAgg(self.mem.fig, master=self.mem.graph)
        self.mem.canvas.draw()
        self.mem.canvas.get_tk_widget().pack()


if __name__ == "__main__":
    # import python_ta
    # python_ta.check_all(config={
    #    'max-line-length': 120,
    #    'disable': ['E1136'],
    #    'extra-imports': ['csv', 'networkx', 'sqlite3', 'collections', 'matplotlib.pyplot'],
    #    'allowed-io': ['load_review_graph'],
    #    'max-nested-blocks': 4
    # })

    print("This is the wrong file. Please run main.py")
