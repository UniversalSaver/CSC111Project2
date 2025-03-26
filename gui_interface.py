"""
A file with functions for creating the window which the user will use. Will use tkinter. The buttons will make calls
to functions in graph_processing.py

# TODO - add copyright
"""
import graph_processing as gp
from tkinter.font import Font
from tkinter import Tk, Frame, Label, Button, OptionMenu, Text, StringVar, PhotoImage
from tkinter import ttk
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time

class App():
    root: Tk
    font: Font
    width: int
    height: int
    type: StringVar
    name1: StringVar
    name2: StringVar
    statusWindow: Text
    graphWindow: Label

    def __init__(self):
        self.root = Tk()
        self.root.title("Created by Tai Poole, Nabhan Rashid, and Danny Tran")
        screenWidth = self.root.winfo_screenwidth()
        screenHeight = self.root.winfo_screenheight()
        self.width = int(screenWidth / 4 * 3)
        self.height = int(screenHeight / 4 * 3)
        centerX = int(screenWidth / 2 - self.width / 2)
        centerY = int(screenHeight / 2 - self.height / 2)
        self.root.geometry(f'{self.width}x{self.height}+{centerX}+{centerY}')
        self.font = Font(family="Comic Sans MS", size=15) #TODO please do not let this be in comic sans

        self.initInput(self.root)
        self.initActor(self.root)

    def run(self):
        self.root.mainloop()

    def initInput(self, mainFrame):
        inputFrame = Frame(mainFrame, bg='blue', bd=15, width=self.width/3)

        self.initInfo(inputFrame)
        self.initField(inputFrame)

        inputFrame.pack(side=tk.LEFT, fill=tk.BOTH)
        inputFrame.pack_propagate(False)

    def initInfo(self, inputFrame):
        infoFrame = Frame(inputFrame, bg='green', bd=15)
        title = ttk.Label(infoFrame, font=self.font, wraplength=(self.width/3)-50, justify=tk.CENTER, text="The really cool connected thing TODO NAME")
        description = (ttk.Label(infoFrame, font=self.font, wraplength=(self.width/3)-50, justify=tk.CENTER,
            text="This is a really cool thing that will connect actors to movies. she kevin on my bacon till i 6 degrees or less")) #probably make this a text box?
        infoFrame.pack(side=tk.TOP, fill=tk.BOTH)
        title.pack(side=tk.TOP)
        description.pack(side=tk.TOP)

    def initField(self, inputFrame):
        fieldFrame = Frame(inputFrame, bd=15)

        self.initName1(fieldFrame)
        self.initName2(fieldFrame)
        self.initSearch(fieldFrame)
        self.initDbg(fieldFrame)

        fieldFrame.pack(fill=tk.BOTH, expand=True)

    def initName1(self, fieldFrame):
        name1Frame = Frame(fieldFrame, bd=15)
        name1Label = ttk.Label(name1Frame, font=self.font, text="Starting actor's name: ")
        self.name1 = StringVar(self.root)
        name1Input = ttk.Entry(name1Frame, textvariable=self.name1)

        name1Frame.pack(expand=True)
        name1Label.pack()
        name1Input.pack()

    def initName2(self, fieldFrame):
        name2Frame = Frame(fieldFrame, bd=15)
        name2Label = ttk.Label(name2Frame, font=self.font, text="Ending actor's name: ")
        self.name2 = StringVar(self.root)
        name2Input = ttk.Entry(name2Frame, textvariable=self.name2)

        name2Frame.pack(expand=True)
        name2Label.pack()
        name2Input.pack()

    def initSearch(self, fieldFrame):
        searchFrame = Frame(fieldFrame, bd=15)
        dropdownFrame = Frame(searchFrame, bd=15)
        searchLabel = ttk.Label(dropdownFrame, font=self.font, text="Search type: ")
        self.type = StringVar(self.root)
        self.type.set("Fast")
        typeBox = OptionMenu(dropdownFrame, self.type, "Fast", "Short")
        searchButton = Button(searchFrame, command=self.doTheThing, font=self.font, text="Go!")

        searchFrame.pack(expand=True)
        dropdownFrame.pack(side=tk.LEFT)
        searchLabel.pack()
        typeBox.pack()
        searchButton.pack(side=tk.RIGHT)

    def initDbg(self, fieldFrame):
        dbgFrame = Frame(fieldFrame, bd=15)
        self.statusWindow = Text(dbgFrame, font=self.font)
        self.statusWindow.insert(tk.END, "")
        self.statusWindow.config(state=tk.DISABLED)

        dbgFrame.pack()
        self.statusWindow.pack()

    def initActor(self, mainFrame):
        global angryBaby
        angryBaby = PhotoImage(file="angrybaby.png")
        actorFrame = Frame(mainFrame, bg='red')
        self.actorWindow = Label(actorFrame, image=angryBaby)
        self.actorWindow.pack(expand=True)

        actorFrame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def doTheThing(self):
        name1 = self.name1.get()
        name2 = self.name2.get()
        searchType = self.type.get()
        try:
            self.statusWindow.config(state=tk.NORMAL)
            self.statusWindow.delete('1.0', tk.END)
            self.statusWindow.insert(tk.END, "Searching...")
            self.statusWindow.config(state=tk.DISABLED)
            startTime = time.time()
            info = doNothing(name1, name2, searchType) #TODO this will be the gp function call
            #depends on implementation but probably something like?
            waitTime = round(time.time() - startTime, 2)
            if info[0]:
                self.statusWindow.config(state=tk.NORMAL)
                self.statusWindow.delete('1.0', tk.END)
                self.statusWindow.insert(tk.END, f"Found {searchType} connection in \n{waitTime} seconds and {info[2]} steps")
                self.statusWindow.config(state=tk.DISABLED)

                fig = plt.figure(figsize=(10, 10), dpi=100) #theoretically this should be screen size agnostic but not sure
                y = [x for x in range(100)]
                plot = fig.add_subplot(111)
                plot.plot(y)
                canvas = FigureCanvasTkAgg(fig, master = self.actorWindow)
                canvas.draw()
                canvas.get_tk_widget().pack()
            else:
                self.statusWindow.config(state=tk.NORMAL)
                self.statusWindow.delete('1.0', tk.END)
                self.statusWindow.insert(tk.END, "No connection found :(")
                self.statusWindow.config(state=tk.DISABLED)
        except: #custom error class that calls when they call a faulty actor?
            self.statusWindow.config(state=tk.NORMAL)
            self.statusWindow.delete('1.0', tk.END)
            self.statusWindow.insert(tk.END, "Sorry, that actor doesn't exist")
            self.statusWindow.config(state=tk.DISABLED)

def doNothing(name1, name2, searchType):
    time.sleep(0.3)
    return [True, 0, 0]

if __name__ == "__main__":
    app = App()
    app.run()


# TODO - I don't know enough about tkinter to know what type of functions or classes are necessary to use it. Whoever
# wants to do this. Call and we can discuss the format
#
# '''fieldFrame = Frame(inputFrame, bd=15)

'''name1Frame = Frame(fieldFrame, bd=15)
name1Label = ttk.Label(name1Frame, font=self.font, text="Starting actor's name: ")
name1Input = ttk.Entry(name1Frame)

name2Frame = Frame(fieldFrame, bd=15)
name2Label = ttk.Label(name2Frame, font=self.font, text="Ending actor's name: ")
name2Input = ttk.Entry(name2Frame)

searchFrame = Frame(fieldFrame, bd=15)
dropdownFrame = Frame(searchFrame, bd=15)
searchLabel = ttk.Label(dropdownFrame, font=self.font, text="Search type: ")
type = StringVar(self.root)
type.set("Fast")
typeBox = OptionMenu(dropdownFrame, type, "Fast", "Short")
searchButton = Button(searchFrame, font=self.font, text="Go!")

dbgFrame = Frame(fieldFrame, bd=15)
dbgWindow = Text(dbgFrame, state=tk.DISABLED, font=self.font)




actorFrame = Frame(self.root, bg='red')

actorFrame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
angryBaby = PhotoImage(file="angrybaby.png")
actorLabel = ttk.Label(actorFrame, image=angryBaby)
actorLabel.pack(expand=True)

inputFrame.pack(side=tk.LEFT, fill=tk.BOTH)
inputFrame.pack_propagate(False)



fieldFrame.pack(fill=tk.BOTH, expand=True)

name1Frame.pack(expand=True)
name1Label.pack()
name1Input.pack()

name2Frame.pack(expand=True)
name2Label.pack()
name2Input.pack()

searchFrame.pack(expand=True)
dropdownFrame.pack(side=tk.LEFT)
searchLabel.pack()
typeBox.pack()
searchButton.pack(side=tk.RIGHT)

dbgFrame.pack()
dbgWindow.pack()
dbgWindow.insert(tk.END, "This is the little box that says when it worked/error messages (wrong name) etc")'''
