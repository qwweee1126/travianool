# -*- coding: utf-8 -*-
#include parent path in sys.path
import os.path, threading, time, random, datetime
from Tkinter import *
from tkMessageBox import *

sys.path.append(os.path.normpath(os.getcwd()+'/..'))

from common.TravianConfig import TravianConfig
from common.TravianClient import TravianClient
from datetime import datetime, timedelta
import common.util as util

#global
STOP = False
THREADS = []

#The main window    
class AutoAttackWindow(Tk):    
    def __init__(self):
        Tk.__init__(self)
        
        #登陆信息 
        f1 = Frame(self)
        Label(f1, text=u'用户名').pack(side=LEFT)
        self.userEnt = Entry(f1, width=15)
        self.userEnt.insert(END, u'灶君')
        self.userEnt.pack(side=LEFT)
        
        Label(f1, text=u'密码').pack(side=LEFT)
        self.passEnt = Entry(f1, width=15)
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
        Label(f2, text='出兵类型').pack(side=LEFT)
        self.cEnt = Entry(f2, width=5)
        self.cEnt.insert(END, 4)
        self.cEnt.pack(side=LEFT)
        f2.pack()

        #等待时间
        Label(f2, text='等待(秒)').pack(side=LEFT)
        self.waitEnt = Entry(f2, width=5)
        self.waitEnt.insert(END, 2)
        self.waitEnt.pack(side=LEFT)
        f2.pack()
        
        #kid: 村庄id
        f2 = Frame(self)
        Label(f2, text=u'村  庄  id      ').pack(side=LEFT)
        self.kidEnt = Entry(f2, width=30)
        self.kidEnt.pack(side=LEFT)
        f2.pack()

        #
        f2 = Frame(self)
        Label(f2, text=u'单程时间(秒)').pack(side=LEFT)
        self.timeEnt = Entry(f2, width=30)
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
        for i in range(6, 12):
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
        self.config = TravianConfig(self.userEnt.get().encode('cp936'), self.passEnt.get())
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
            params['c'] = int(self.cEnt.get())
            kids = [int(k) for k in self.kidEnt.get().split()]      #村庄id可以多个, 用空格分开
            times = [int(t) for t in self.timeEnt.get().split()]    #停顿秒数对应到村庄的时间，空格分开
            for i in range(1, 12):
                params['t%s'%i] = int(self.armyEnts[i-1].get())
            wait = int(self.waitEnt.get())    #停顿秒数对应到村庄的时间，空格分开
        except:
            showerror('数据验证错误', '请确认您输入的数据正确')
            return
        
        if len(kids) != len(times):
            showerror('村庄数必须和时间数一致', '村庄数必须和时间数一致')
            return
        
        #开线程提交数据
        global STOP
        STOP = False
        for i in range(len(kids)):
            name = u'TD-%s'%kids[i]
            thread = AutoThread(name, self.tclient, params.copy(), kids[i], times[i]*2 + 60, wait) #需要用params.copy(), 一个线程一份参数
            THREADS.append(thread)
            thread.start()
        
    def stop(self):
        global STOP
        STOP = True
#        for thread in THREADS:
#            thread
        sys.exit(0)     #退出所有线程
        

class AutoThread(threading.Thread):
    def __init__(self, name, tclient, params, kid, sleepSec, wait=10):
        threading.Thread.__init__(self, name=name)
        self.tclient = tclient
        self.params = params
        self.params['kid'] = kid
        self.sleepSec = sleepSec
        self.URL = 'http://%s/a2b.php'%self.tclient.config.ServerName
        self.wait = wait
        
    def run(self):
        while not STOP:
            #等待时间
            now = datetime.now()
            d = timedelta(seconds=self.wait)
            util.info(u'现在时间%s 等待%s, 在%s出兵'%(now, d, now+d)) 
            time.sleep(self.wait + random.randint(1, 20))   #修正1-20秒
            #can login?
            if not self.tclient.login():
                util.error(u'你没有登陆')
                break
            
            #params 在多线程中共享
            self.params['a'] = random.randint(1, 60000)     #某个随机数
            #post
            self.tclient.doPost(self.URL, self.params)
            util.info(u'%s 完成出兵%s任务, 等待%s秒开始下一轮。'%(self.getName(), self.params['kid'], self.sleepSec))
            time.sleep(self.sleepSec)
        util.info(u'所有任务完成, 退出.')
        
if __name__ == '__main__':
    win = AutoAttackWindow()
    win.mainloop()
