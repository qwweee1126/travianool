# -*- coding: utf-8 -*-
from Tkinter import *
import time, datetime

resourceLabels = {1: u'木', 2:u'泥', 3:u'铁', 4:u'粮'}

class MyFrame(Frame):
    def __init__(self, master, labelTxt):
        Frame.__init__(self, master)
        Label(self, text=labelTxt).pack(side=LEFT)
        self.entries = []
        self.pack()
        
        for i in range(1, 5):
            photo = PhotoImage(file="img/%s.gif" % i)
            label = Label(self, image=photo)
            label.photo = photo
            label.pack(side=LEFT)
            
            ent = Entry(self, width=5)
            ent.pack(side=LEFT)
            self.entries.append(ent)
        

def makeWidgets(win):
    resourceFrame = MyFrame(win, u'资   源')
    reqireFrame = MyFrame(win, u'需    求')
    speedFrame = MyFrame(win, u'生产力')
    
    reportField = Text(win, width=50, height=10)
    reportField.pack()
    
    def getReport():
        reports = []
        for i in range(1, 5):
            try:
                res = int(resourceFrame.entries[i-1].get())
                req = int(reqireFrame.entries[i-1].get())
                speed = int(speedFrame.entries[i-1].get())
            except:
                print 'int error '
            
            r = report(res, req, speed)
            if not r:
                reports.append(u'%s:资源足够'%resourceLabels[i])
            else:
                reports.append(u'%s:缺少%4s, 需要%20s , 至%20s'%(resourceLabels[i], r[0], r[1], r[2]))
            
        reportField.delete(1.0, END)
        print reports
        reportField.insert(END, '\n'.join(reports))
        
    repBtn = Button(win, text=u'计算', command=getReport)
    repBtn.pack()

def report(resource, require, speed):
    """Return None if meet requirement, or (gap, timedelta, when)."""
    
    if resource >= require:
        return None
    else:
        gap = require - resource
        seconds = int(float(gap)/speed*3600)     #in seconds
        
        
        when = datetime.datetime(2008, 9, 1)            #datetime obj
        when = when.fromtimestamp(time.time() + seconds)    #datetime obj
        
        return (gap, datetime.timedelta(seconds=seconds), when.strftime('%m-%d %H:%M'))

    
if __name__ == '__main__':
    win = Tk()
    makeWidgets(win)
    win.mainloop()