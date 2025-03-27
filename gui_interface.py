"""
A file with functions for creating the window which the user will use. Will use tkinter. The buttons will make calls
to functions in graph_processing.py

# TODO - add copyright
"""
import time
from tkinter.font import Font
from tkinter import Tk, Frame, Label, Button, OptionMenu, Text, StringVar, PhotoImage
from tkinter import ttk
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import graph_processing as gp


class App():
    '''
    A class to represent the GUI for the user to interact with the program.

    Instance Attributes:
        root: the main window of the application
        font: the font to be used in the application
        dimensions: the dimensions of the window (found during init, depend on screen size)
        type: stores an item that holds the type of search to be done
        names: a list of 2 items that hold the names of the actors to be searched
        status_window: the place in the window that holds the text box (lock/unlock purposes)
        actor_window: the place in the window that holds the actor image
        db_path: the path to the database file
    '''
    root: Tk
    font: Font
    dimensions: tuple[int, int]
    type: StringVar
    names: list[StringVar]
    status_window: Text
    actor_window: Label
    db_path: str

    def __init__(self, path: str) -> None:
        self.root = Tk()
        self.root.title("Created by Tai Poole, Nabhan Rashid, and Danny Tran")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.dimensions = (int(screen_width / 4 * 3), int(screen_height / 4 * 3))
        center_x = int(screen_width / 2 - self.dimensions[0] / 2)
        center_y = int(screen_height / 2 - self.dimensions[1] / 2)
        self.root.geometry(f'{self.dimensions[0]}x{self.dimensions[1]}+{center_x}+{center_y}')
        self.font = Font(family="Apple Symbols", size=18)  # shouldve been comic sans -T
        self.db_path = path
        self.names = []

        self.init_input(self.root)
        self.init_actor(self.root)

    def run(self) -> None:
        '''
        Runs the application
        '''
        self.root.mainloop()

    def init_input(self, main_frame: Tk) -> None:
        '''
        Initializes the input frame (left side of the window)
        '''
        input_frame = Frame(main_frame, bg='blue', bd=15, width=self.dimensions[0] / 3)

        self.init_info(input_frame)
        self.init_field(input_frame)

        input_frame.pack(side=tk.LEFT, fill=tk.BOTH)
        input_frame.pack_propagate(False)

    def init_info(self, input_frame: Frame) -> None:
        '''
        Initializes the info frame (top left side of the window)
        '''
        info_frame = Frame(input_frame, bg='green', bd=15)
        title = ttk.Label(info_frame, font=self.font, wraplength=(self.dimensions[0] / 3) - 50, justify=tk.CENTER,
                          text="The really cool connected thing TODO NAME")
        description = ttk.Label(info_frame, font=self.font, wraplength=(self.dimensions[0] / 3) - 50, justify=tk.CENTER,
                                text="This is a really cool thing that will connect actors to movies. she kevin on my bacon till i 6 degrees or less")
        info_frame.pack(side=tk.TOP, fill=tk.BOTH)
        title.pack(side=tk.TOP)
        description.pack(side=tk.TOP)

    def init_field(self, input_frame: Frame) -> None:
        '''
        Initializes the field frame (bottom left side of the window)
        '''
        field_frame = Frame(input_frame, bd=15)

        self.init_name1(field_frame)
        self.init_name2(field_frame)
        self.init_search(field_frame)
        self.init_dbg(field_frame)

        field_frame.pack(fill=tk.BOTH, expand=True)

    def init_name1(self, field_frame: Frame) -> None:
        '''
        Initializes the first name input frame
        '''
        name1_frame = Frame(field_frame, bd=15)
        name1_label = ttk.Label(name1_frame, font=self.font, text="Starting actor's name: ")
        self.names.append(StringVar(self.root))
        name1_input = ttk.Entry(name1_frame, textvariable=self.names[0])

        name1_frame.pack(expand=True)
        name1_label.pack()
        name1_input.pack()

    def init_name2(self, field_frame: Frame) -> None:
        '''
        Initializes the second name input frame
        '''
        name2_frame = Frame(field_frame, bd=15)
        name2_label = ttk.Label(name2_frame, font=self.font, text="Ending actor's name: ")
        self.names.append(StringVar(self.root))
        name2_input = ttk.Entry(name2_frame, textvariable=self.names[1])

        name2_frame.pack(expand=True)
        name2_label.pack()
        name2_input.pack()

    def init_search(self, field_frame: Frame) -> None:
        '''
        Initializes the search input frame, including search type and search button
        '''
        search_frame = Frame(field_frame, bd=15)
        dropdown_frame = Frame(search_frame, bd=15)
        search_label = ttk.Label(dropdown_frame, font=self.font, text="Search type: ")
        self.type = StringVar(self.root)
        self.type.set("Fast")
        type_box = OptionMenu(dropdown_frame, self.type, "Fast", "Short")
        search_button = Button(search_frame, command=self.doTheThing, font=self.font, text="Go!")

        search_frame.pack(expand=True)
        dropdown_frame.pack(side=tk.LEFT)
        search_label.pack()
        type_box.pack()
        search_button.pack(side=tk.RIGHT)

    def init_dbg(self, field_frame: Frame) -> None:
        '''
        Initializes the debug frame, for displaying the status of the search
        '''
        dbg_frame = Frame(field_frame, bd=15)
        self.status_window = Text(dbg_frame, font=self.font)
        self.status_window.insert(tk.END, "")
        self.status_window.config(state=tk.DISABLED)

        dbg_frame.pack()
        self.status_window.pack()

    def init_actor(self, main_frame: Tk) -> None:
        '''
        Initializes the actor frame (right side of window)
        '''
        global angryBaby
        angryBaby = PhotoImage(file="angrybaby.png")
        actor_frame = Frame(main_frame, bg='red')
        self.actor_window = Label(actor_frame, image=angryBaby)
        self.actor_window.pack(expand=True)

        actor_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def doTheThing(self) -> None:
        name1 = self.names[0].get()
        name2 = self.names[1].get()
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
                wait_time = round(time.time() - start_time, 3)

                self.status_window.config(state=tk.NORMAL)
                self.status_window.delete('1.0', tk.END)
                degrees = int((len(path) - 1) / 2)
                msg = f"Found {search_type} connection in \n {wait_time} seconds and {degrees} degrees of seperation"
                self.status_window.insert(tk.END, msg)
                self.status_window.config(state=tk.DISABLED)

                fig = plt.figure(figsize=(10, 10), dpi=100)
                plot = fig.add_subplot(111)
                pos = nx.spring_layout(info)
                colours = [info.nodes[k]['color'] for k in info.nodes]
                nx.draw(info, pos, node_color=colours, ax=plot)
                canvas = FigureCanvasTkAgg(fig, master=self.actor_window)
                canvas.draw()
                canvas.get_tk_widget().pack()
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


if __name__ == "__main__":
    import python_ta

    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['E1136'],
        'extra-imports': ['csv', 'networkx', 'sqlite3', 'collections', 'matplotlib.pyplot'],
        'allowed-io': ['load_review_graph'],
        'max-nested-blocks': 4
    })
    #app = App("./small_data_files/small_db.db")
    #app.run()
