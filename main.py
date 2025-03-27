"""
The main file, where anything necessary will be run. This will likely be mostly the tkinter call

TODO - add copyright
"""
import gui_interface

if __name__ == '__main__':
    #TODO something to do with choosing the data? im not sure
    app = gui_interface.App("small_data_files/small database.db")
    app.run()
