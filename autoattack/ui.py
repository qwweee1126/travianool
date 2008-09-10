# -*- coding: utf-8 -*-
#include parent path in sys.path
import os.path, threading, time, random
from Tkinter import *
from tkMessageBox import *

sys.path.append(os.path.normpath(os.getcwd()+'/..'))

from common.TravianConfig import TravianConfig
from common.TravianClient import TravianClient
 
class MyThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    
    def run(self):
        print 'i am tired'
        time.sleep(5)
        print 'get up now'
        
    
def newthread():
    print 'start new thread'
    MyThread().start()

STOP = False

#The main window    
class AutoAttackWindow(Tk):    
    def __init__(self):
        Tk.__init__(self)
        
        #登陆信息 
        f1 = Frame(self)
        Label(f1, text=u'用户名').pack(side=LEFT)
        self.userEnt = Entry(f1, width=15)
        self.userEnt.insert(END, u'testool')
        self.userEnt.pack(side=LEFT)
        
        Label(f1, text=u'密码').pack(side=LEFT)
        self.passEnt = Entry(f1, width=15)
        self.passEnt.insert(END, '111111')
        self.passEnt.pack(side=LEFT)
        
        f1.pack()
        
        #杂项
        f2 = Frame(self)

        #id: 不知道这是什么
        Label(f2, text='ID').pack(side=LEFT)
        self.idEnt = Entry(f2, width=5)
        self.idEnt.insert(END, 39)
        self.idEnt.pack(side=LEFT)
        
        #c: 出兵方式 - 2增援, 3攻击:普通/侦察, 4攻击:抢夺
        Label(f2, text=u'出兵方式').pack(side=LEFT)
        self.cEnt = Entry(f2, width=5)
        self.cEnt.insert(END, 4)
        self.cEnt.pack(side=LEFT)
        
        #kid: 村庄id
        Label(f2, text=u'村庄id').pack(side=LEFT)
        self.kidEnt = Entry(f2, width=7)
        self.kidEnt.pack(side=LEFT)

        #
        Label(f2, text=u'单程时间(秒)').pack(side=LEFT)
        self.timeEnt = Entry(f2, width=8)
        self.timeEnt.pack(side=LEFT)
        
        f2.pack()
        
        #兵力
        self.armyEnts = []

        f3 = Frame(self)
        for i in range(1, 6):
            photo = PhotoImage(file="img/%s.gif" % i)
            label = Label(f3, image=photo)
            label.photo = photo
            label.pack(side=LEFT)
            
            ent = Entry(f3, width=5)
            ent.pack(side=LEFT)
            ent.insert(END, 0)
            self.armyEnts.append(ent)
        f3.pack()

        f4 = Frame(self)
        for i in range(6, 11):
            photo = PhotoImage(file="img/%s.gif" % i)
            label = Label(f4, image=photo)
            label.photo = photo
            label.pack(side=LEFT)
            
            ent = Entry(f4, width=5)
            ent.insert(END, 0)
            ent.pack(side=LEFT)
            self.armyEnts.append(ent)
        f4.pack()
        
        Button(self, text=u'发兵', command=self.go).pack(side=LEFT)
        Button(self, text=u'暂停', command=self.stop).pack(side=LEFT)
    
    #登陆
    def login(self):
        self.config = TravianConfig(self.userEnt.get(), self.passEnt.get())
        self.config.ReLogin = True
        
        self.tclient = TravianClient(self.config)
        if not self.tclient.login():
            return False
        return True
    
    def go(self):
        #先登陆
        if not self.login():
            showerror('无法登陆', '请确认用户名和密码正确')
            return
        
        #数据验证
        try:
            params = {}
            params['id'] = int(self.idEnt.get())
            params['a'] = random.randint(1, 60000)
            params['c'] = int(self.cEnt.get())
            params['kid'] = int(self.kidEnt.get())
            time = int(self.timeEnt.get())
            for i in range(1, 11):
                params['t%s'%i] = int(self.armyEnts[i-1].get())
            params['t11'] = 0
        except:
            showerror('数据验证错误', '请确认您输入的数据正确')
            return
        
        #开线程提交数据
        global STOP
        STOP = False
        t = AutoThread(self.tclient, params, time*2 + 60)
        t.start()
        
    def stop(self):
        global STOP
        STOP = True
        

class AutoThread(threading.Thread):
    def __init__(self, tclient, params, sleepSec):
        threading.Thread.__init__(self)
        self.tclient = tclient
        self.params = params
        self.sleepSec = sleepSec
        self.URL = 'http://%s/a2b.php'%self.tclient.config.ServerName
        
    def run(self):
        while not STOP:
            #can login?
            if not self.tclient.login():
                break
            print 'has loginned'
            
            #post
            print 'job dont and sleep :', threading.currentThread()
            self.tclient.doPost(self.URL, self.params)
            time.sleep(self.sleepSec)
            print 'thread wake up'
        print 'all work done'

        
if __name__ == '__main__':
    win = AutoAttackWindow()
    win.mainloop()