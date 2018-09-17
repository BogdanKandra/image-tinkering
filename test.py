"""
Created on Wed Sep 12 21:34:01 2018

@author: Bogdan
"""
#from tkinter import Frame, Button, Tk
from tkinter import *

class Window(Frame):
    
    def __init__(self, master=None):
        Frame.__init__(self)
        
        self.init_window()
        
    def init_window(self):
        self.master.title('HELLO TKINTER') # Set the window title
        self.pack(fill=BOTH, expand=1)
        
#        quitButton = Button(self, text='Quit', command=self.app_exit)
#        quitButton.place(x=0, y=0)
        
        myMenu = Menu(self.master) # Define a menu for the main window
        self.master.config(menu=myMenu)
        
        fileMenu = Menu(myMenu) # Define a menu for the main window menu
        fileMenu.add_command(label='Exit', command=self.app_exit) # Add an Exit command to the File menu
        myMenu.add_cascade(label='File', menu=fileMenu) # Add the File menu to the main menu
        
        
    def app_exit(self):
        self.master.destroy()
        
mainWindow = Tk()
mainWindow.geometry('800x600')
app = Window(mainWindow)
mainWindow.mainloop()
