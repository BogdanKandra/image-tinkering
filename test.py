"""
Created on Wed Sep 12 21:34:01 2018

@author: Bogdan
"""
from tkinter import *

class Window(Frame):
    
    def __init__(self, master=None):
        Frame.__init__(self)
        
        self.init_window()
        
    def init_window(self):
        self.master.title('HELLO TKINTER')
        self.pack(fill=BOTH, expand=1)
        quitButton = Button(self, text='Quit')
        quitButton.place(x=0, y=0)
        
mainWindow = Tk()
mainWindow.geometry('400x300')
app = Window(mainWindow)
mainWindow.mainloop()
