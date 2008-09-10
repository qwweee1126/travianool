#some ui component
from Tkinter import *

#provide a label and entry component
class LabelEntry(Frame):
    """Construct a label entry frame"""
    def __init__(self, master, label, entryValue='', entryWidth=15):
        Frame.__init__(self, master)
        Label(self, text=label).pack(side=LEFT)
        self.entry = Entry(self, width=entryWidth)
        if entryValue:
            self.entry.insert(END, entryValue)
        self.entry.pack(side=LEFT)
        self.pack()
    def getValue(self):
        return self.entry.get()