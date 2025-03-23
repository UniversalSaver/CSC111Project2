"""
A file with functions for creating the window which the user will use. Will use tkinter. The buttons will make calls
to functions in graph_processing.py

# TODO - add copyright
"""
import graph_processing as gp
from tkinter.font import Font
from tkinter import *
from tkinter import ttk

root = Tk()
root.title("Created by Tai Poole, Nabhan Rashid, and Danny Tran")
screenWidth = root.winfo_screenwidth()
screenHeight = root.winfo_screenheight()
windowWidth = int(screenWidth / 4 * 3)
windowHeight = int(screenHeight / 4 * 3)
centerX = int(screenWidth / 2 - windowWidth / 2)
centerY = int(screenHeight / 2 - windowHeight / 2)
root.geometry(f'{windowWidth}x{windowHeight}+{centerX}+{centerY}')
root.resizable(True, True)

font = Font(family="Comic Sans MS", size=15) #TODO please do not let this be in comic sans

'''s = ttk.Style()
s.configure('TFrame', background='red')
s.configure('actorWindow.TFrame', background='blue')
s.configure('inputWindow.TFrame', background='green')'''

inputFrame = Frame(root, bg='blue', bd=15, width=windowWidth/3)

infoFrame = Frame(inputFrame, bg='green', bd=15)
title = ttk.Label(infoFrame, font=font, wraplength=(windowWidth/3)-50, justify=CENTER, text="The really cool connected thing TODO NAME")
description = ttk.Label(infoFrame, font=font, wraplength=(windowWidth/3)-50, justify=CENTER, text="This is a really cool thing that will connect actors to movies. she kevin on my bacon till i 6 degrees or less")

fieldFrame = Frame(inputFrame, bd=15)

name1Frame = Frame(fieldFrame, bd=15)
name1Label = ttk.Label(name1Frame, font=font, text="Starting actor's name: ")
name1Input = ttk.Entry(name1Frame)

name2Frame = Frame(fieldFrame, bd=15)
name2Label = ttk.Label(name2Frame, font=font, text="Ending actor's name: ")
name2Input = ttk.Entry(name2Frame)

searchFrame = Frame(fieldFrame, bd=15)
dropdownFrame = Frame(searchFrame, bd=15)
searchLabel = ttk.Label(dropdownFrame, font=font, text="Search type: ")
type = StringVar(root)
type.set("Fast")
typeBox = OptionMenu(dropdownFrame, type, "Fast", "Short")
searchButton = Button(searchFrame, font=font, text="Go!")

dbgFrame = Frame(fieldFrame, bd=15)
dbgWindow = ttk.Label(dbgFrame, font=font, text="This is the little box that says when it worked/error messages (wrong name) etc")



actorFrame = Frame(root, bg='red')

actorFrame.pack(side=RIGHT, fill=BOTH, expand=True)
angryBaby = PhotoImage(file="angrybaby.png")
actorLabel = ttk.Label(actorFrame, image=angryBaby)
actorLabel.pack(expand=True)

inputFrame.pack(side=LEFT, fill=BOTH)
inputFrame.pack_propagate(False)

infoFrame.pack(side=TOP, fill=BOTH)
title.pack(side=TOP)
description.pack(side=TOP)

fieldFrame.pack(fill=BOTH, expand=True)

name1Frame.pack(expand=True)
name1Label.pack()
name1Input.pack()

name2Frame.pack(expand=True)
name2Label.pack()
name2Input.pack()

searchFrame.pack(expand=True)
dropdownFrame.pack(side=LEFT)
searchLabel.pack()
typeBox.pack()
searchButton.pack(side=RIGHT)

dbgFrame.pack()
dbgWindow.pack()

root.mainloop()


# TODO - I don't know enough about tkinter to know what type of functions or classes are necessary to use it. Whoever
# wants to do this. Call and we can discuss the format
