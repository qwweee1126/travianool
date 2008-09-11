# -*- coding: utf-8 -*-
from Tkinter import *
from tkMessageBox import showerror
import os.path, time, datetime, re

sys.path.append(os.path.normpath(os.getcwd()+'/..'))

from common.TravianConfig import TravianConfig
from common.TravianClient import TravianClient

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
    def __login():
        #注意:config.UserName保存的是str类型的字符, 所以从Entry.get()过来的unicode需要encode
        config = TravianConfig(userEnt.get().encode('cp936'), passEnt.get().encode('cp936'))
        config.ReLogin = True
        
        tclient = TravianClient(config)
        if not tclient.login():
            showerror('登陆错误', '请确认用户名和密码正确')
            return
        
        #get data
        theurl = 'http://%s/dorf1.php'%(config.ServerName)
        html = tclient.getHtmlByURL(theurl)
        for i in range(4, 0, -1):
            matObj = re.findall('<td id=l%s title=(\d+)>(\d+)/\d+</td>'%i, html)
            if not matObj:
                showerror('取数据出错', '取数据出错')
                return
            
            #delete
            resourceFrame.entries[4-i].delete(0, END)
            resourceFrame.entries[4-i].insert(END, matObj[0][1])
            speedFrame.entries[4-i].delete(0, END)
            speedFrame.entries[4-i].insert(END, matObj[0][0])
        #
        
    #登陆
    loginFrame = Frame(win)
    Label(loginFrame, text='用户名').pack(side=LEFT)
    userEnt = Entry(loginFrame, width=10)
    userEnt.pack(side=LEFT)
    Label(loginFrame, text='密码').pack(side=LEFT)
    passEnt = Entry(loginFrame, width=10)
    passEnt.pack(side=LEFT)
    Button(loginFrame, text='取得资源数据', command=__login).pack(side=LEFT)
    loginFrame.pack()
    ##########################################
    
    resourceFrame = MyFrame(win, u'资   源')
    speedFrame = MyFrame(win, u'生产力')
    
    reqFrame = Frame(win)
    Label(reqFrame, text='需    求').pack(side=LEFT)
    reqEnt = Entry(reqFrame, width=30)
    reqEnt.pack(side=LEFT)
    reqFrame.pack()
    
    reportField = Text(win, width=50, height=10)
    reportField.pack()
    
    def getReport():
        reports = []
        req = [int(s) for s in reqEnt.get().split('|')]
        for i in range(1, 5):
            try:
                res = int(resourceFrame.entries[i-1].get())
                speed = int(speedFrame.entries[i-1].get())
#                req = int(reqireFrame.entries[i-1].get())
            except:
                showerror('数据错误', '请确认数据格式正确')
                return
            
            r = report(res, speed, req[i-1])
            if len(r)==1:
                reports.append(u'%s:资源足够. 盈余:%s'%(resourceLabels[i], r[0]))
            else:
                reports.append(u'%s:缺少%4s, 需要%15s , 至%12s'%(resourceLabels[i], r[0], r[1], r[2]))
            
        reportField.delete(1.0, END)
        reportField.insert(END, '\n'.join(reports))
        
    repBtn = Button(win, text=u'计算', command=getReport)
    repBtn.pack()

def report(resource, speed, require):
    """Return None if meet requirement, or (gap, timedelta, when)."""
    
    if resource >= require:
        return [resource - require]
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