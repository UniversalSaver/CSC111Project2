"""
The main file, where anything necessary will be run. This will likely be mostly the tkinter call

Copyright and Usage Information
===============================
This file is solely provided for the use in grading and review of the named student's
work by the TAs and Professors of CSC111. All further distribution of this code whether
as is or modified is firmly prohibited.

This file is Copyright (c) Nabhan Rashid, Danny Tran, and Tai Poole

"""
import gui_interface

if __name__ == '__main__':
    app = gui_interface.App("./data_files/actors_and_movies.db")
    app.run()
